# Testing DSAHub Locally

There are three ways to test the app locally, from zero-setup to full-stack.
Pick the one that matches what you need.

| Method | What it tests | Needs Docker? | Needs Postgres/Redis? | Time |
|--------|--------------|---------------|----------------------|------|
| [**1. Smoke tests**](#method-1-smoke-tests-zero-setup) | All service logic (31 tests) | ❌ No | ❌ No | 10 sec |
| [**2. Docker Compose**](#method-2-docker-compose-full-stack) | Full stack incl. Kong gateway | ✅ Yes | (bundled) | 2 min |
| [**3. Manual**](#method-3-manual-service-by-service) | Full stack, no Docker | ❌ No | ✅ Yes | 5 min |

---

## Method 1: Smoke tests (zero setup)

This runs 31 end-to-end tests against all four services using **SQLite + a fake
Redis** — no Docker, no PostgreSQL, no Redis, no Node required. It validates every
endpoint: auth, courses, quizzes, progress, leaderboard.

### Prerequisites
- Python 3.12+ (your `.venv` already has all dependencies)

### Run

```bash
cd /Users/saibhargav/Documents/MyProjects/dsa
source .venv/bin/activate
python run_tests.py
```

### What you should see

```
Seeding database...
Seeded 12 topics with lessons.
Seeded 12 quizzes with questions.
[OK] Database seeded (courses + quizzes + all tables)

=== Auth Service ===
  [OK] register new user
  [OK] register returns token
  [OK] duplicate email -> 409
  [OK] login success
  [OK] wrong password -> 401
  [OK] GET /auth/me
  [OK] internal verify

=== Course Service ===
  [OK] list topics
  [OK] topics have lessons
  ... (9 tests)

=== Quiz Service ===
  ... (8 tests)

=== Progress Service ===
  ... (7 tests)

==================================================
Total: 31   Passed: 31   Failed: 0

ALL TESTS PASSED!
```

### What it covers
- **Auth (7 tests):** register, login, duplicate rejection, wrong password, token
  validation, internal verify endpoint
- **Course (9 tests):** topic listing, topic detail, lessons, Markdown content, code
  blocks, search, 404 handling, content richness (28 lessons)
- **Quiz (8 tests):** listing, by-topic filter, detail, correct-answer hiding,
  submission, scoring, per-question details, explanations
- **Progress (7 tests):** lesson completion, progress retrieval, quiz attempts, stats,
  leaderboard, unauthenticated rejection

> This is the fastest way to verify the backend works. It does **not** test Kong,
> the frontend SPA, or real PostgreSQL/Redis.

---

## Method 2: Docker Compose (full stack)

This brings up the **entire system**: PostgreSQL, Redis, all four FastAPI services,
and the Kong gateway — exactly as it runs in production, but locally.

### Prerequisites
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed and running

### Run

```bash
cd /Users/saibhargav/Documents/MyProjects/dsa
docker compose up --build
```

Wait ~30 seconds for all services to start. The first run builds images and seeds the
database. You'll see logs like:
```
kong         | [kong-entrypoint] all upstream hostports resolved successfully
course-service | Uvicorn running on http://0.0.0.0:4002
quiz-service   | Seeded 12 quizzes with questions.
```

### Test the API (through Kong on port 8080)

```bash
# 1. Health check — is Kong routing?
curl -s http://localhost:8080/courses/topics | python3 -m json.tool | head -20

# 2. Register a user
curl -s -X POST http://localhost:8080/auth/register \
  -H "Content-Type: application/json" \
  -d '{"name":"Alice","email":"alice@example.com","password":"secret123"}' | python3 -m json.tool

# 3. Login and grab the token
TOKEN=$(curl -s -X POST http://localhost:8080/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"alice@example.com","password":"secret123"}' | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")

# 4. Authenticated request (mark a lesson complete)
curl -s -X POST http://localhost:8080/progress/lessons \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"lesson_slug":"arrays-intro","completed":true}' | python3 -m json.tool

# 5. Leaderboard
curl -s http://localhost:8080/progress/leaderboard | python3 -m json.tool
```

### Serve the frontend SPA

The SPA is in `frontend/` and needs to point at Kong. In a **separate terminal**:

```bash
cd /Users/saibhargav/Documents/MyProjects/dsa/frontend

# Point the SPA at the local Kong gateway
echo 'window.__API_BASE__ = "http://localhost:8080";' > config.js

# Serve the static files (Python's built-in server, no Node needed)
python3 -m http.server 3000
```

Open **http://localhost:3000** in your browser. You should see the DSAHub home page
with 12 topic cards. Register, browse courses, read a lesson, take a quiz.

### Stop

```bash
# In the docker compose terminal (or another terminal):
docker compose down          # stop containers
docker compose down -v       # stop + delete the database volume (fresh start)
```

---

## Method 3: Manual (service-by-service, no Docker)

Use this if you don't have Docker but want to run the real stack with real PostgreSQL
and Redis. You'll run each service in its own terminal.

### Prerequisites
- Python 3.12+ (your `.venv`)
- PostgreSQL running locally
- Redis running locally

#### Install PostgreSQL and Redis (if needed)

```bash
brew install postgresql@16 redis
brew services start postgresql@16
brew services start redis
```

#### Create the database

```bash
createdb dsalearning
# or: psql -c "CREATE DATABASE dsalearning;"
```

### Terminal 1 — Auth service (port 4001)

```bash
cd /Users/saibhargav/Documents/MyProjects/dsa
source .venv/bin/activate
cd auth-service
export DATABASE_URL="postgresql://$(whoami)@localhost:5432/dsalearning"
export REDIS_URL="redis://localhost:6379"
export JWT_SECRET="dev-secret-change-me-in-production"
uvicorn main:app --port 4001 --reload
```

### Terminal 2 — Course service (port 4002)

```bash
cd /Users/saibhargav/Documents/MyProjects/dsa
source .venv/bin/activate
cd course-service
export DATABASE_URL="postgresql://$(whoami)@localhost:5432/dsalearning"
export REDIS_URL="redis://localhost:6379"
uvicorn main:app --port 4002 --reload
```

> The course service auto-seeds 12 topics + 28 lessons on first startup.

### Terminal 3 — Quiz service (port 4003)

```bash
cd /Users/saibhargav/Documents/MyProjects/dsa
source .venv/bin/activate
cd quiz-service
export DATABASE_URL="postgresql://$(whoami)@localhost:5432/dsalearning"
export REDIS_URL="redis://localhost:6379"
uvicorn main:app --port 4003 --reload
```

> The quiz service auto-seeds 12 quizzes + 47 questions on first startup.

### Terminal 4 — Progress service (port 4004)

```bash
cd /Users/saibhargav/Documents/MyProjects/dsa
source .venv/bin/activate
cd progress-service
export DATABASE_URL="postgresql://$(whoami)@localhost:5432/dsalearning"
export REDIS_URL="redis://localhost:6379"
export AUTH_SERVICE_URL="http://localhost:4001"
uvicorn main:app --port 4004 --reload
```

### Terminal 5 — Kong gateway (port 8080)

Kong needs Docker to run, so if you're in the no-Docker scenario, you have two options:

**Option A — Skip Kong, hit services directly.** Test each service on its own port:

```bash
curl -s http://localhost:4001/health    # auth
curl -s http://localhost:4002/courses/topics | python3 -m json.tool | head
curl -s http://localhost:4003/quizzes | python3 -m json.tool | head
curl -s http://localhost:4004/health    # progress
```

**Option B — Use the old Node gateway** (in `gateway-old/`). It does the same routing
as Kong but runs with Node. You'd need Node installed:

```bash
cd /Users/saibhargav/Documents/MyProjects/dsa/gateway-old
npm install
export AUTH_SERVICE_URL=http://localhost:4001
export COURSE_SERVICE_URL=http://localhost:4002
export QUIZ_SERVICE_URL=http://localhost:4003
export PROGRESS_SERVICE_URL=http://localhost:4004
npm start
```

Then the gateway is on **http://localhost:8080**.

### Terminal 6 — Frontend SPA

```bash
cd /Users/saibhargav/Documents/MyProjects/dsa/frontend

# Point at whichever gateway you're using
echo 'window.__API_BASE__ = "http://localhost:8080";' > config.js

python3 -m http.server 3000
```

Open **http://localhost:3000**.

---

## Quick reference: ports

| Port | What |
|------|------|
| 3000 | Frontend SPA (Python http.server) |
| 4001 | Auth service (direct) |
| 4002 | Course service (direct) |
| 4003 | Quiz service (direct) |
| 4004 | Progress service (direct) |
| 8080 | Kong gateway (Docker) / Node gateway |
| 5432 | PostgreSQL |
| 6379 | Redis |

---

## Quick reference: which method to use

| You want to... | Use |
|----------------|-----|
| Quickly verify the backend logic works | **Method 1** (10 seconds) |
| Test the full system including Kong + browser | **Method 2** (Docker) |
| Develop/debug a single service with `--reload` | **Method 3** (manual) |
| Test the Kong gateway config specifically | **Method 2** (Docker) |
| Verify the Render deployment will work | **Method 2**, then check the DEPLOYMENT_GUIDE.md |

---

## Troubleshooting

### `docker: command not found`
Docker Desktop isn't installed. Install it from https://www.docker.com/products/docker-desktop/
or use Method 1 (smoke tests) or Method 3 (manual) instead.

### `psql: command not found` or `createdb` fails
PostgreSQL isn't installed. Install with `brew install postgresql@16 && brew services start
postgresql@16`, or use Method 1 (no Postgres needed).

### `redis-cli: command not found`
Redis isn't installed. Install with `brew install redis && brew services start redis`, or use
Method 1 (no Redis needed).

### `node: command not found`
You're trying the Node gateway (Method 3, Option B). Install Node with `brew install node`,
or use Kong (Method 2) or direct service calls (Method 3, Option A) instead.

### Kong returns 502 Bad Gateway
A backend service isn't up yet. Check that all four services show `Uvicorn running on...`
in their logs. Kong's entrypoint logs which hostports it resolved — verify they match.

### Frontend loads but API calls fail
The `config.js` isn't pointing at the right gateway URL. Verify:
```bash
cat frontend/config.js
# Should show: window.__API_BASE__ = "http://localhost:8080";
```

### Database is empty after Docker restart
The volume persists across `docker compose down` (without `-v`). To get a fresh database:
```bash
docker compose down -v    # delete the volume
docker compose up --build  # rebuild and re-seed
```

### Port already in use
```bash
lsof -i :8080   # find what's using the port
kill -9 <PID>    # kill it
```
