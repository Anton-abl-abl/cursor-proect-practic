import os
from collections.abc import Generator
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.engine import URL, Engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATABASE_PATH = DATA_DIR / "notes.db"
ENV_PATH = BASE_DIR / ".env"


class Base(DeclarativeBase):
    pass


def _load_env(path: Path) -> None:
    if not path.is_file():
        return
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


def _database_url() -> str:
    _load_env(ENV_PATH)
    configured = os.environ.get("DATABASE_URL", "").strip()
    if not configured:
        return ""
    if configured.startswith("postgres://"):
        configured = "postgresql://" + configured.removeprefix("postgres://")
    if configured.startswith("postgresql://"):
        return "postgresql+psycopg://" + configured.removeprefix("postgresql://")
    if configured.startswith("postgresql+psycopg://"):
        return configured
    raise RuntimeError(
        "DATABASE_URL должен начинаться с postgresql://. "
        "Скопируйте строку Session pooler в настройках базы Supabase."
    )


def _create_engine() -> Engine:
    url = _database_url()
    if url:
        return create_engine(url, pool_pre_ping=True)
    return create_engine(
        URL.create("sqlite", database=str(DATABASE_PATH)),
        connect_args={"check_same_thread": False},
    )


engine = _create_engine()
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def get_db() -> Generator[Session, None, None]:
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


def init_db() -> None:
    if engine.dialect.name == "sqlite":
        DATA_DIR.mkdir(parents=True, exist_ok=True)
    from app import models  # noqa: F401

    Base.metadata.create_all(bind=engine)
