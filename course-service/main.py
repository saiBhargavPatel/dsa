import time
from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel
from sqlalchemy import desc

from config import get_db, engine, Base, SessionLocal, settings
from models import Topic, Lesson
from seed import seed as seed_db
import redis as redis_lib
import json

app = FastAPI(title="Course Service", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

redis_client = redis_lib.from_url(settings.redis_url)


@app.on_event("startup")
def on_startup():
    Topic.__table__.create(engine, checkfirst=True)
    Lesson.__table__.create(engine, checkfirst=True)
    # Auto-seed if empty
    db = SessionLocal()
    if db.query(Topic).count() == 0:
        seed_db(db)
    db.close()


# ---------- Schemas ----------
class TopicOut(BaseModel):
    id: int
    slug: str
    title: str
    description: str
    icon: str | None
    order_index: int
    difficulty: str
    lesson_count: int

    class Config:
        from_attributes = True


class LessonSummary(BaseModel):
    id: int
    slug: str
    title: str
    summary: str
    duration_minutes: int
    order_index: int

    class Config:
        from_attributes = True


class LessonOut(BaseModel):
    id: int
    slug: str
    title: str
    summary: str
    content_md: str
    duration_minutes: int
    order_index: int
    topic_id: int
    topic_title: str | None = None
    topic_slug: str | None = None

    class Config:
        from_attributes = True


# ---------- Routes ----------
@app.get("/health")
def health():
    return {"service": "course", "status": "ok", "time": time.time()}


@app.get("/courses/topics", response_model=list[TopicOut])
def list_topics(db: Session = Depends(get_db)):
    cache_key = "topics:all"
    cached = redis_client.get(cache_key)
    if cached:
        return json.loads(cached)
    topics = db.query(Topic).order_by(Topic.order_index).all()
    result = []
    for t in topics:
        result.append(TopicOut(
            id=t.id, slug=t.slug, title=t.title, description=t.description,
            icon=t.icon, order_index=t.order_index, difficulty=t.difficulty,
            lesson_count=len(t.lessons),
        ).model_dump())
    redis_client.setex(cache_key, 300, json.dumps(result))
    return result


@app.get("/courses/topics/{slug}", response_model=TopicOut)
def get_topic(slug: str, db: Session = Depends(get_db)):
    t = db.query(Topic).filter(Topic.slug == slug).first()
    if not t:
        raise HTTPException(404, "Topic not found")
    return TopicOut(
        id=t.id, slug=t.slug, title=t.title, description=t.description,
        icon=t.icon, order_index=t.order_index, difficulty=t.difficulty,
        lesson_count=len(t.lessons),
    )


@app.get("/courses/topics/{slug}/lessons", response_model=list[LessonSummary])
def list_lessons(slug: str, db: Session = Depends(get_db)):
    t = db.query(Topic).filter(Topic.slug == slug).first()
    if not t:
        raise HTTPException(404, "Topic not found")
    return [LessonSummary.model_validate(l) for l in t.lessons]


@app.get("/courses/lessons/{slug}", response_model=LessonOut)
def get_lesson(slug: str, db: Session = Depends(get_db)):
    cache_key = f"lesson:{slug}"
    cached = redis_client.get(cache_key)
    if cached:
        return json.loads(cached)
    l = db.query(Lesson).filter(Lesson.slug == slug).first()
    if not l:
        raise HTTPException(404, "Lesson not found")
    out = LessonOut(
        id=l.id, slug=l.slug, title=l.title, summary=l.summary,
        content_md=l.content_md, duration_minutes=l.duration_minutes,
        order_index=l.order_index, topic_id=l.topic_id,
        topic_title=l.topic.title, topic_slug=l.topic.slug,
    ).model_dump()
    redis_client.setex(cache_key, 300, json.dumps(out))
    return out


@app.post("/courses/admin/seed")
def admin_seed(db: Session = Depends(get_db)):
    seed_db(db)
    redis_client.flushdb()
    return {"message": "Seeded successfully"}


@app.get("/courses/search")
def search(q: str = Query(..., min_length=1), db: Session = Depends(get_db)):
    """Full-text-ish search across topics and lessons."""
    like = f"%{q.lower()}%"
    topics = db.query(Topic).filter(Topic.title.ilike(like) | Topic.description.ilike(like)).all()
    lessons = db.query(Lesson).filter(
        Lesson.title.ilike(like) | Lesson.summary.ilike(like) | Lesson.content_md.ilike(like)
    ).all()
    return {
        "topics": [{"id": t.id, "slug": t.slug, "title": t.title, "icon": t.icon} for t in topics],
        "lessons": [{"id": l.id, "slug": l.slug, "title": l.title, "topic_slug": l.topic.slug}
                    for l in lessons],
    }
