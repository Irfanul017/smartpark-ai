"""SQLite database configuration for SmartPark AI."""

from __future__ import annotations

import os
from collections.abc import Generator

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker


DATABASE_URL = os.getenv("SMARTPARK_DATABASE_URL", "sqlite:///./smartpark.db")
_connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=_connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    """Base class for database models."""


def get_db() -> Generator[Session, None, None]:
    """Provide one SQLAlchemy session for a request."""
    database = SessionLocal()
    try:
        yield database
    finally:
        database.close()


def init_database() -> None:
    """Create development tables and perform the one additive SQLite upgrade."""
    # Import registers all model classes after Base is defined, without circular imports.
    from app import models  # noqa: F401

    Base.metadata.create_all(bind=engine)
    if DATABASE_URL.startswith("sqlite"):
        session_columns = {column["name"] for column in inspect(engine).get_columns("parking_sessions")}
        if "user_id" not in session_columns:
            with engine.begin() as connection:
                connection.execute(text("ALTER TABLE parking_sessions ADD COLUMN user_id INTEGER"))
        slot_columns = {column["name"] for column in inspect(engine).get_columns("parking_slots")}
        if "is_reserved" not in slot_columns:
            with engine.begin() as connection:
                connection.execute(text("ALTER TABLE parking_slots ADD COLUMN is_reserved BOOLEAN NOT NULL DEFAULT 0"))
