"""SQLAlchemy infrastructure only: no domain schema or automatic table creation."""

from collections.abc import Iterator
from contextlib import contextmanager
from typing import Annotated

from fastapi import Depends, Request
from sqlalchemy import Engine, create_engine, event, text
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import DEFAULT_DATABASE_PATH, DEFAULT_DATABASE_URL, Settings


class Base(DeclarativeBase):
    """Future ORM models will extend this base after requirements are reviewed."""


def create_db_engine(settings: Settings) -> Engine:
    if settings.database_url == DEFAULT_DATABASE_URL:
        DEFAULT_DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)

    # SQLite permits request handling across FastAPI's worker threads.
    # PostgreSQL and other engines do not receive this SQLite-specific argument.
    connect_args = (
        {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}
    )
    engine = create_engine(settings.database_url, connect_args=connect_args, pool_pre_ping=True)
    if engine.dialect.name == "sqlite":

        @event.listens_for(engine, "connect")
        def sqlite_options(connection, _record):
            cursor = connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.execute("PRAGMA busy_timeout=10000")
            cursor.close()

    return engine


def create_session_factory(engine: Engine) -> sessionmaker[Session]:
    return sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def get_engine(request: Request) -> Engine:
    """A dependency that tests can override without touching the development database."""
    return request.app.state.engine


def get_session(request: Request) -> Iterator[Session]:
    with request.app.state.session_factory() as session:
        yield session


DbSession = Annotated[Session, Depends(get_session)]


@contextmanager
def write_session(request: Request) -> Iterator[Session]:
    """Lock before reading eligibility/conflicts and keep it through commit."""
    with request.app.state.session_factory() as db:
        try:
            db.execute(text("BEGIN IMMEDIATE"))
            yield db
            db.commit()
        except BaseException:
            db.rollback()
            raise
