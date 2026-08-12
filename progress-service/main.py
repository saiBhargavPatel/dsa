import time
from fastapi import FastAPI, Depends, HTTPException, Header, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from pydantic import BaseModel
from typing import List, Optional
import httpx
import redis as redis_lib

from config import get_db, engine, Base, SessionLocal, settings
from models import LessonProgress, QuizAttempt

app = FastAPI(title="Progress Service", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

redis_client = redis_lib.from_url(settings.redis_url)


@app.on_event("startup")
def on_startup():
    LessonProgress.__table__.create(engine, checkfirst=True)
    QuizAttempt.__table__.create(engine, checkfirst=True)


# ---------- Auth helper ----------
async def get_user_id(authorization: Optional[str] = Header(None)) -> int:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(401, "Missing token")
    token = authorization.split(" ", 1)[1]
    # Try cache first
    cached = redis_client.get(f"auth:{token}")
    if cached:
        return int(cached)
    # Verify with auth-service
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            r = await client.get(f"{settings.auth_service_url}/internal/verify",
                                 params={"token": token})
        if r.status_code != 200:
            raise HTTPException(401, "Invalid or expired token")
        uid = r.json()["user_id"]
        redis_client.setex(f"auth:{token}", 120, str(uid))
        return uid
    except httpx.HTTPError:
        raise HTTPException(503, "Auth service unavailable")


# ---------- Schemas ----------
class LessonProgressIn(BaseModel):
    lesson_slug: str
    completed: bool = True


class QuizAttemptIn(BaseModel):
    quiz_id: int
    topic_slug: str
    score: float
    correct: int
    total: int


class LeaderboardEntry(BaseModel):
    user_id: int
    name: str | None = None
    total_score: float
    attempts: int
    lessons_completed: int


class StatsOut(BaseModel):
    lessons_completed: int
    quizzes_taken: int
    best_avg_score: float
    recent_attempts: list


# ---------- Routes ----------
@app.get("/health")
def health():
    return {"service": "progress", "status": "ok", "time": time.time()}


@app.post("/progress/lessons")
async def mark_lesson(
    body: LessonProgressIn,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_user_id),
):
    existing = db.query(LessonProgress).filter(
        LessonProgress.user_id == user_id,
        LessonProgress.lesson_slug == body.lesson_slug,
    ).first()
    if existing:
        existing.completed = body.completed
        existing.completed_at = func.now() if body.completed else None
    else:
        from datetime import datetime
        db.add(LessonProgress(
            user_id=user_id,
            lesson_slug=body.lesson_slug,
            completed=body.completed,
            completed_at=datetime.utcnow() if body.completed else None,
        ))
    db.commit()
    redis_client.delete(f"user:{user_id}:stats")
    return {"message": "Progress saved", "completed": body.completed}


@app.get("/progress/lessons")
async def my_lessons(
    db: Session = Depends(get_db),
    user_id: int = Depends(get_user_id),
):
    rows = db.query(LessonProgress).filter(LessonProgress.user_id == user_id).all()
    return {"completed_lessons": [r.lesson_slug for r in rows if r.completed],
            "all": [{"lesson_slug": r.lesson_slug, "completed": r.completed} for r in rows]}


@app.post("/progress/quizzes")
async def record_quiz(
    body: QuizAttemptIn,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_user_id),
):
    attempt = QuizAttempt(
        user_id=user_id,
        quiz_id=body.quiz_id,
        topic_slug=body.topic_slug,
        score=body.score,
        correct=body.correct,
        total=body.total,
    )
    db.add(attempt)
    db.commit()
    db.refresh(attempt)
    redis_client.delete(f"user:{user_id}:stats")
    return {"message": "Quiz attempt recorded", "attempt_id": attempt.id}


@app.get("/progress/quizzes")
async def my_quiz_attempts(
    db: Session = Depends(get_db),
    user_id: int = Depends(get_user_id),
):
    rows = db.query(QuizAttempt).filter(
        QuizAttempt.user_id == user_id
    ).order_by(desc(QuizAttempt.created_at)).all()
    return {"attempts": [{"id": a.id, "quiz_id": a.quiz_id, "topic_slug": a.topic_slug,
                          "score": a.score, "correct": a.correct, "total": a.total,
                          "created_at": a.created_at.isoformat() if a.created_at else None}
                         for a in rows]}


@app.get("/progress/stats")
async def my_stats(
    db: Session = Depends(get_db),
    user_id: int = Depends(get_user_id),
):
    cached = redis_client.get(f"user:{user_id}:stats")
    if cached:
        import json
        return json.loads(cached)
    lessons_done = db.query(LessonProgress).filter(
        LessonProgress.user_id == user_id, LessonProgress.completed == True
    ).count()
    attempts = db.query(QuizAttempt).filter(QuizAttempt.user_id == user_id).all()
    avg = sum(a.score for a in attempts) / len(attempts) if attempts else 0
    recent = sorted(attempts, key=lambda x: x.created_at or "", reverse=True)[:5]
    stats = {
        "lessons_completed": lessons_done,
        "quizzes_taken": len(attempts),
        "best_avg_score": round(avg, 2),
        "recent_attempts": [{"quiz_id": a.quiz_id, "topic_slug": a.topic_slug,
                             "score": a.score, "correct": a.correct, "total": a.total}
                            for a in recent],
    }
    import json
    redis_client.setex(f"user:{user_id}:stats", 60, json.dumps(stats))
    return stats


@app.get("/progress/leaderboard")
async def leaderboard(db: Session = Depends(get_db)):
    cache_key = "leaderboard:all"
    cached = redis_client.get(cache_key)
    if cached:
        import json
        return json.loads(cached)
    # Aggregate best score per user per quiz, then sum
    best = db.query(
        QuizAttempt.user_id,
        func.max(QuizAttempt.score).label("best"),
    ).group_by(QuizAttempt.user_id, QuizAttempt.quiz_id).subquery()

    agg = db.query(
        best.c.user_id,
        func.sum(best.c.best).label("total_score"),
        func.count().label("attempts"),
    ).group_by(best.c.user_id).order_by(desc("total_score")).limit(20).all()

    # lessons completed per user
    lessons = db.query(
        LessonProgress.user_id,
        func.count(LessonProgress.id).label("lc")
    ).filter(LessonProgress.completed == True).group_by(LessonProgress.user_id).all()
    lesson_map = {r.user_id: r.lc for r in lessons}

    result = [{"user_id": r.user_id, "total_score": float(r.total_score or 0),
               "attempts": int(r.attempts), "lessons_completed": lesson_map.get(r.user_id, 0)}
              for r in agg]
    import json
    redis_client.setex(cache_key, 120, json.dumps(result))
    return result
