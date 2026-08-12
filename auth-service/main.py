from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.exc import IntegrityError
import redis as redis_lib
import json
import time

from config import get_db, engine, Base, settings
from models import User
from security import hash_password, verify_password, create_access_token, decode_token

app = FastAPI(title="Auth Service", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# Redis for token blacklist + rate-limiting
_redis = redis_lib.from_url(settings.redis_url)


@app.on_event("startup")
def on_startup():
    # Create tables owned by this service
    User.__table__.create(engine, checkfirst=True)


# ---------- Schemas ----------
class RegisterIn(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    email: EmailStr
    password: str = Field(min_length=6, max_length=128)


class LoginIn(BaseModel):
    email: EmailStr
    password: str


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: "UserOut"


class UserOut(BaseModel):
    id: int
    email: str
    name: str
    is_admin: bool

    class Config:
        from_attributes = True


TokenOut.model_rebuild()


# ---------- Helpers ----------
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    payload = decode_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    user_id = int(payload.get("sub", 0))
    # check blacklist (logout)
    if _redis.get(f"bl:{token}"):
        raise HTTPException(status_code=401, detail="Token revoked")
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user


# ---------- Routes ----------
@app.get("/health")
def health():
    return {"service": "auth", "status": "ok", "time": time.time()}


@app.post("/auth/register", response_model=TokenOut, status_code=201)
def register(body: RegisterIn, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == body.email).first()
    if existing:
        raise HTTPException(status_code=409, detail="Email already registered")
    user = User(
        email=body.email,
        name=body.name,
        hashed_password=hash_password(body.password),
    )
    db.add(user)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Email already registered")
    db.refresh(user)
    token = create_access_token(user.id)
    return TokenOut(access_token=token, user=UserOut.model_validate(user))


@app.post("/auth/login", response_model=TokenOut)
def login(body: LoginIn, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == body.email).first()
    if not user or not verify_password(body.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    token = create_access_token(user.id)
    return TokenOut(access_token=token, user=UserOut.model_validate(user))


@app.get("/auth/me", response_model=UserOut)
def me(current: User = Depends(get_current_user)):
    return UserOut.model_validate(current)


@app.post("/auth/logout")
def logout(token: str = Depends(oauth2_scheme)):
    payload = decode_token(token)
    if payload:
        exp = payload.get("exp", int(time.time()) + 3600)
        ttl = max(int(exp - time.time()), 1)
        _redis.setex(f"bl:{token}", ttl, "1")
    return {"message": "Logged out"}


# Internal endpoint for other services to validate tokens
@app.get("/internal/verify")
def internal_verify(token: str, db: Session = Depends(get_db)):
    payload = decode_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    if _redis.get(f"bl:{token}"):
        raise HTTPException(status_code=401, detail="Token revoked")
    user_id = int(payload.get("sub", 0))
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return {"user_id": user.id, "email": user.email, "name": user.name, "is_admin": user.is_admin}
