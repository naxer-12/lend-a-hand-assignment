"""
Database Configuration & Session Management
--------------------------------------------
Provides SQLAlchemy 2.0 compatible engine, declarative base, and session lifecycle.
Gracefully handles both PostgreSQL for production and SQLite for local evaluation.
"""

from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from app.config import settings

# SQLite compatibility adjustment
connect_args = {}
if settings.DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(
    settings.DATABASE_URL,
    connect_args=connect_args,
    pool_pre_ping=True,
    echo=False
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db() -> Generator:
    """
    FastAPI dependency yielding a thread-safe database session.
    Automatically rolls back on uncaught errors and closes after request completion.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """Initializes tables in database."""
    Base.metadata.create_all(bind=engine)
