"""
End-to-end smoke test for all DSA Learning Platform services.

Each service has identically-named files (config.py, models.py, main.py, seed.py),
so we isolate imports by clearing sys.modules between services. All services share
a file-based SQLite database (mimicking the shared PostgreSQL in production).
"""
import os
import sys
import tempfile
import shutil

# ---- 1. Environment: shared file-based SQLite ----
TMPDIR = tempfile.mkdtemp()
DB_PATH = os.path.join(TMPDIR, "test.db")
DB_URL = f"sqlite:///{DB_PATH}"

os.environ["DATABASE_URL"] = DB_URL
os.environ["REDIS_URL"] = "redis://fake"
os.environ["JWT_SECRET"] = "test-secret"
os.environ["AUTH_SERVICE_URL"] = "http://127.0.0.1:4001"
os.environ["PORT"] = "4000"

# ---- 2. Fake Redis ----
class FakeRedis:
    def __init__(self):
        self.store = {}
    def get(self, k):
        v = self.store.get(k)
        return v.encode() if isinstance(v, str) else v
    def setex(self, k, ttl, v):
        self.store[k] = v
    def set(self, k, v):
        self.store[k] = v
    def delete(self, k):
        self.store.pop(k, None)
    def flushdb(self):
        self.store.clear()

import redis as _redis_module
_redis_module.from_url = lambda url, **kw: FakeRedis()

# ---- 3. Helpers ----
BASE = os.path.dirname(os.path.abspath(__file__))

def clear_modules():
    for name in list(sys.modules.keys()):
        if name in ("config", "models", "main", "seed", "security"):
            del sys.modules[name]

def set_service_path(svc):
    svc_path = os.path.join(BASE, svc)
    sys.path[:] = [p for p in sys.path if os.path.join(BASE, "auth-service") not in p
                   and os.path.join(BASE, "course-service") not in p
                   and os.path.join(BASE, "quiz-service") not in p
                   and os.path.join(BASE, "progress-service") not in p]
    sys.path.insert(0, svc_path)

def load_service(svc):
    clear_modules()
    set_service_path(svc)
    import importlib
    return importlib.import_module("main")

results = []
def test(name, condition, detail=""):
    status = "PASS" if condition else "FAIL"
    results.append((name, condition, detail))
    print(f"  [{'OK' if condition else 'XX'}] {name}" + (f" -- {detail}" if detail and not condition else ""))

# ---- 4. Seed courses and quizzes FIRST ----
print("Seeding database...")
clear_modules()
set_service_path("course-service")
import config as cfg
import models as cm
cm.Base.metadata.create_all(cfg.engine)
from seed import seed as seed_courses
import config
db = config.SessionLocal()
seed_courses(db)
db.close()

clear_modules()
set_service_path("quiz-service")
import config as qcfg
import models as qm
qm.Base.metadata.create_all(qcfg.engine)
from seed import seed as seed_quizzes
import config
db = config.SessionLocal()
seed_quizzes(db)
db.close()

# Create auth + progress tables
for svc in ["auth-service", "progress-service"]:
    clear_modules()
    set_service_path(svc)
    import config, models
    models.Base.metadata.create_all(config.engine)

print("[OK] Database seeded (courses + quizzes + all tables)\n")

# ---- 5. Test each service ----
from fastapi.testclient import TestClient

# === AUTH SERVICE ===
print("=== Auth Service ===")
auth_mod = load_service("auth-service")
auth_c = TestClient(auth_mod.app)

r = auth_c.post("/auth/register", json={"name": "Test Student", "email": "s@t.com", "password": "secret123"})
test("register new user", r.status_code == 201, f"status={r.status_code}")
token = r.json().get("access_token") if r.status_code == 201 else None
test("register returns token", bool(token))

r = auth_c.post("/auth/register", json={"name": "X", "email": "s@t.com", "password": "secret123"})
test("duplicate email -> 409", r.status_code == 409)

r = auth_c.post("/auth/login", json={"email": "s@t.com", "password": "secret123"})
test("login success", r.status_code == 200)
token = r.json().get("access_token") if r.status_code == 200 else token

r = auth_c.post("/auth/login", json={"email": "s@t.com", "password": "wrong"})
test("wrong password -> 401", r.status_code == 401)

r = auth_c.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
test("GET /auth/me", r.status_code == 200 and r.json()["email"] == "s@t.com")

r2 = auth_c.post("/auth/register", json={"name": "Student Two", "email": "t@t.com", "password": "secret123"})
token2 = r2.json().get("access_token")

r = auth_c.get("/internal/verify", params={"token": token})
test("internal verify", r.status_code == 200 and r.json()["email"] == "s@t.com")

# === COURSE SERVICE ===
print("\n=== Course Service ===")
course_mod = load_service("course-service")
course_c = TestClient(course_mod.app)

r = course_c.get("/courses/topics")
test("list topics", r.status_code == 200 and len(r.json()) >= 10, f"count={len(r.json())}")
topics = r.json() if r.status_code == 200 else []
test("topics have lessons", all(t["lesson_count"] > 0 for t in topics) if topics else False)

r = course_c.get("/courses/topics/arrays")
test("get arrays topic", r.status_code == 200 and "Arrays" in r.json()["title"])

r = course_c.get("/courses/topics/arrays/lessons")
test("list arrays lessons", r.status_code == 200 and len(r.json()) >= 3, f"count={len(r.json()) if r.status_code==200 else 0}")
lesson_slug = r.json()[0]["slug"] if r.status_code == 200 and r.json() else None

r = course_c.get(f"/courses/lessons/{lesson_slug}")
test("get lesson detail", r.status_code == 200 and len(r.json()["content_md"]) > 100)
test("lesson has code blocks", "```" in r.json().get("content_md", ""))

r = course_c.get("/courses/search?q=binary")
test("search works", r.status_code == 200 and (len(r.json()["topics"]) + len(r.json()["lessons"])) > 0)

r = course_c.get("/courses/topics/nope")
test("404 for missing topic", r.status_code == 404)

total_lessons = sum(t["lesson_count"] for t in topics)
test(f"rich content ({total_lessons} lessons)", total_lessons >= 25, f"got {total_lessons}")

# === QUIZ SERVICE ===
print("\n=== Quiz Service ===")
quiz_mod = load_service("quiz-service")
quiz_c = TestClient(quiz_mod.app)

r = quiz_c.get("/quizzes")
test("list quizzes", r.status_code == 200 and len(r.json()) >= 10, f"count={len(r.json())}")
quizzes = r.json() if r.status_code == 200 else []
quiz_id = quizzes[0]["id"] if quizzes else None

r = quiz_c.get("/quizzes/by-topic/arrays")
test("quizzes by topic", r.status_code == 200 and len(r.json()) >= 1)

r = quiz_c.get(f"/quizzes/{quiz_id}")
test("get quiz detail", r.status_code == 200 and len(r.json()["questions"]) >= 1)
quiz_detail = r.json() if r.status_code == 200 else {}
test("correct_index NOT exposed", all("correct_index" not in q for q in quiz_detail.get("questions", [])))

answers = [{"question_id": q["id"], "selected_index": 0} for q in quiz_detail.get("questions", [])]
r = quiz_c.post(f"/quizzes/{quiz_id}/submit", json={"answers": answers})
test("submit quiz", r.status_code == 200)
if r.status_code == 200:
    res = r.json()
    test("result has score 0-100", 0 <= res["score"] <= 100)
    test("result has per-question details", len(res["details"]) == len(quiz_detail["questions"]))
    test("details include explanations", any(d.get("explanation") for d in res["details"]))

# === PROGRESS SERVICE ===
print("\n=== Progress Service ===")
progress_mod = load_service("progress-service")
import main as _prog_main

async def _patched_get_user_id(request: _prog_main.Request):
    authorization = request.headers.get("authorization")
    if not authorization or not authorization.startswith("Bearer "):
        raise _prog_main.HTTPException(401, "Missing token")
    tok = authorization.split(" ", 1)[1]
    cached = _prog_main.redis_client.get(f"auth:{tok}")
    if cached:
        return int(cached)
    r = auth_c.get("/internal/verify", params={"token": tok})
    if r.status_code != 200:
        raise _prog_main.HTTPException(401, "Invalid token")
    uid = r.json()["user_id"]
    _prog_main.redis_client.setex(f"auth:{tok}", 120, str(uid))
    return uid

_prog_main.app.dependency_overrides[_prog_main.get_user_id] = _patched_get_user_id
progress_c = TestClient(_prog_main.app)

hdr = {"Authorization": f"Bearer {token}"}

r = progress_c.post("/progress/lessons", json={"lesson_slug": "arrays-intro", "completed": True}, headers=hdr)
test("mark lesson complete", r.status_code == 200, f"status={r.status_code} body={r.text}")

r = progress_c.get("/progress/lessons", headers=hdr)
test("get lesson progress", r.status_code == 200 and "arrays-intro" in r.json().get("completed_lessons", []), f"body={r.text}")

r = progress_c.post("/progress/quizzes", json={"quiz_id": quiz_id, "topic_slug": "arrays", "score": 80.0, "correct": 4, "total": 5}, headers=hdr)
test("record quiz attempt", r.status_code == 200, f"status={r.status_code}")

r = progress_c.get("/progress/quizzes", headers=hdr)
test("get quiz attempts", r.status_code == 200 and len(r.json()["attempts"]) >= 1)

r = progress_c.get("/progress/stats", headers=hdr)
test("get stats", r.status_code == 200 and r.json()["lessons_completed"] >= 1, f"body={r.text}")

hdr2 = {"Authorization": f"Bearer {token2}"}
progress_c.post("/progress/quizzes", json={"quiz_id": quiz_id, "topic_slug": "arrays", "score": 60.0, "correct": 3, "total": 5}, headers=hdr2)

r = progress_c.get("/progress/leaderboard")
test("leaderboard", r.status_code == 200 and len(r.json()) >= 2, f"count={len(r.json()) if r.status_code==200 else 0}")

r = progress_c.get("/progress/lessons")
test("unauthenticated -> 401", r.status_code == 401)

# ---- 6. Summary ----
print("\n" + "=" * 50)
passed = sum(1 for _, c, _ in results if c)
failed = sum(1 for _, c, _ in results if not c)
print(f"Total: {len(results)}   Passed: {passed}   Failed: {failed}")
if failed:
    print("\nFailed:")
    for name, c, detail in results:
        if not c:
            print(f"  FAIL: {name}: {detail}")
else:
    print("\nALL TESTS PASSED!")

shutil.rmtree(TMPDIR, ignore_errors=True)
sys.exit(1 if failed else 0)
