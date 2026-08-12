from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql://dsauser:dsapass@localhost:5432/dsalearning"
    redis_url: str = "redis://localhost:6379"
    auth_service_url: str = "http://auth-service:4001"

    class Config:
        env_file = ".env"


def _normalize_url(url: str) -> str:
    """Ensure auth_service_url has a scheme.

    Render's `fromService: property: hostport` returns `host:port` with no
    scheme (e.g. `auth-service-ab1c:10000`). Without http:// the httpx call
    to /internal/verify would treat the hostname as a scheme and fail.
    """
    if url.startswith("http://") or url.startswith("https://"):
        return url
    return f"http://{url}"


settings = Settings()
settings.auth_service_url = _normalize_url(settings.auth_service_url)

engine = create_engine(settings.database_url, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
