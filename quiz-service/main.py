import time
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List
import redis as redis_lib
import json

from config import get_db, engine, Base, SessionLocal, settings
from models import Quiz, Question
from seed import seed as seed_db

app = FastAPI(title="Quiz Service", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

redis_client = redis_lib.from_url(settings.redis_url)


@app.on_event("startup")
def on_startup():
    Quiz.__table__.create(engine, checkfirst=True)
    Question.__table__.create(engine, checkfirst=True)
    db = SessionLocal()
    if db.query(Quiz).count() == 0:
        seed_db(db)
    db.close()


# ---------- Schemas ----------
class QuestionOut(BaseModel):
    id: int
    prompt: str
    options: List[str]
    explanation: str | None = None
    order_index: int

    class Config:
        from_attributes = True


class QuestionForAttempt(QuestionOut):
    """Sent to the client — no correct_index."""
    pass


class QuizOut(BaseModel):
    id: int
    topic_slug: str
    title: str
    description: str | None
    question_count: int

    class Config:
        from_attributes = True


class QuizDetail(QuizOut):
    questions: List[QuestionForAttempt]


class AnswerIn(BaseModel):
    question_id: int
    selected_index: int


class SubmissionIn(BaseModel):
    answers: List[AnswerIn]


class ResultOut(BaseModel):
    total: int
    correct: int
    score: float  # percentage
    details: list  # list of per-question result dicts


# ---------- Routes ----------
@app.get("/health")
def health():
    return {"service": "quiz", "status": "ok", "time": time.time()}


@app.get("/quizzes", response_model=list[QuizOut])
def list_quizzes(db: Session = Depends(get_db)):
    quizzes = db.query(Quiz).all()
    return [QuizOut(id=q.id, topic_slug=q.topic_slug, title=q.title,
                    description=q.description, question_count=len(q.questions))
            for q in quizzes]


@app.get("/quizzes/by-topic/{topic_slug}", response_model=list[QuizOut])
def quizzes_by_topic(topic_slug: str, db: Session = Depends(get_db)):
    quizzes = db.query(Quiz).filter(Quiz.topic_slug == topic_slug).all()
    return [QuizOut(id=q.id, topic_slug=q.topic_slug, title=q.title,
                    description=q.description, question_count=len(q.questions))
            for q in quizzes]


@app.get("/quizzes/{quiz_id}", response_model=QuizDetail)
def get_quiz(quiz_id: int, db: Session = Depends(get_db)):
    q = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    if not q:
        raise HTTPException(404, "Quiz not found")
    return QuizDetail(
        id=q.id, topic_slug=q.topic_slug, title=q.title, description=q.description,
        question_count=len(q.questions),
        questions=[QuestionForAttempt(id=qs.id, prompt=qs.prompt, options=qs.options,
                                      explanation=None, order_index=qs.order_index)
                   for qs in q.questions],
    )


@app.post("/quizzes/{quiz_id}/submit", response_model=ResultOut)
def submit_quiz(quiz_id: int, body: SubmissionIn, db: Session = Depends(get_db)):
    q = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    if not q:
        raise HTTPException(404, "Quiz not found")
    questions = {qs.id: qs for qs in q.questions}
    correct_count = 0
    details = []
    for ans in body.answers:
        ques = questions.get(ans.question_id)
        if not ques:
            continue
        is_correct = ans.selected_index == ques.correct_index
        if is_correct:
            correct_count += 1
        details.append({
            "question_id": ques.id,
            "prompt": ques.prompt,
            "selected_index": ans.selected_index,
            "correct_index": ques.correct_index,
            "is_correct": is_correct,
            "explanation": ques.explanation,
        })
    total = len(q.questions)
    score = round((correct_count / total * 100) if total else 0, 2)
    return ResultOut(total=total, correct=correct_count, score=score, details=details)


@app.post("/quizzes/admin/seed")
def admin_seed(db: Session = Depends(get_db)):
    seed_db(db)
    redis_client.flushdb()
    return {"message": "Quizzes seeded successfully"}
