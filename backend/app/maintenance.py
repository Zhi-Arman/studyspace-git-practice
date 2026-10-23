"""Local maintenance: synthetic seed data, retention and consistent SQLite backups."""

import os
import secrets
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from urllib.parse import quote

from sqlalchemy import delete, func, select, text
from sqlalchemy.orm import Session

from app.migration import migrate
from app.models import AuditEvent, Booking, LoginAttempt, LoginSession, Room, Seat, User
from app.security import audit, hash_password, utcnow


def seed_demo(engine) -> dict:
    with Session(engine) as db:
        db.execute(text("BEGIN IMMEDIATE"))
        if db.scalar(select(func.count()).select_from(Room)):
            return {"rooms_created": 0, "seats_created": 0}
        for number, kind in [(1, "STUDY_ROOM"), (2, "CLASSROOM")]:
            letter = "A" if number == 1 else "B"
            room = Room(
                name=f"演示空间 {letter} / Demo {letter}",
                campus="演示校区 / Demo",
                building="图书馆 / Library",
                floor=number + 1,
                kind=kind,
                description="本地教学演示资源 / Local demonstration resource",
                enabled=True,
                opens_at=480,
                closes_at=1320,
            )
            db.add(room)
            db.flush()
            db.add_all(
                [Seat(room_id=room.id, code=f"{letter}{n:02d}", enabled=True) for n in range(1, 7)]
            )
            audit(db, None, "SEED_DEMO", "room", room.id)
        db.commit()
    return {"rooms_created": 2, "seats_created": 12}


def create_admin(engine, username: str, display_name: str, password: str) -> None:
    from app.schemas import Register

    payload = Register(username=username, display_name=display_name, password=password)
    with Session(engine) as db:
        db.execute(text("BEGIN IMMEDIATE"))
        if db.scalar(select(User.id).where(User.username == payload.username)):
            raise ValueError("Username already exists; no account was changed.")
        user = User(
            username=payload.username,
            display_name=payload.display_name,
            password_hash=hash_password(payload.password),
            role="ADMIN",
            enabled=True,
            created_at=utcnow(),
        )
        db.add(user)
        db.flush()
        audit(db, user.id, "CREATE_ADMIN_CLI", "user", user.id)
        db.commit()


def cleanup(engine, now: datetime | None = None) -> dict:
    now = now or utcnow()
    threshold = now - timedelta(days=180)
    with Session(engine) as db:
        db.execute(text("BEGIN IMMEDIATE"))
        expired = db.execute(
            delete(Booking).where(
                ((Booking.cancelled_at.is_not(None)) & (Booking.cancelled_at < threshold))
                | ((Booking.cancelled_at.is_(None)) & (Booking.ends_at < threshold))
            )
        )
        deleted_bookings = expired.rowcount
        events = db.execute(delete(AuditEvent).where(AuditEvent.created_at < threshold)).rowcount
        sessions = db.execute(delete(LoginSession).where(LoginSession.expires_at <= now)).rowcount
        db.execute(
            delete(LoginAttempt).where(LoginAttempt.window_start < now - timedelta(minutes=5))
        )
        candidates = db.scalars(
            select(User).where(
                User.enabled.is_(False),
                User.disabled_at <= now - timedelta(days=30),
                User.anonymized_at.is_(None),
            )
        ).all()
        anonymized = 0
        for user in candidates:
            booking = db.scalar(select(Booking.id).where(Booking.user_id == user.id).limit(1))
            event = db.scalar(select(AuditEvent.id).where(AuditEvent.actor_id == user.id).limit(1))
            if booking is None and event is None:
                user.username = f"deleted_{user.id}_{secrets.token_hex(3)}"
                user.display_name, user.password_hash = "Removed", "!"
                user.anonymized_at = now
                db.execute(delete(LoginSession).where(LoginSession.user_id == user.id))
                anonymized += 1
        db.commit()
    return {
        "deleted_bookings": deleted_bookings,
        "deleted_events": events,
        "expired_sessions": sessions,
        "anonymized_users": anonymized,
    }


def reserve_new_file(path: Path) -> Path:
    path = path.expanduser().absolute()
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor = os.open(path, os.O_CREAT | os.O_EXCL | os.O_RDWR, 0o600)
    os.close(descriptor)
    return path


def backup(engine, output: Path) -> Path:
    if engine.dialect.name != "sqlite":
        raise ValueError("This local version supports SQLite backups only.")
    output = reserve_new_file(output)
    with engine.connect() as connection, sqlite3.connect(output) as target:
        connection.connection.driver_connection.backup(target)
        if target.execute("PRAGMA integrity_check").fetchone()[0] != "ok":
            raise ValueError("Backup integrity check failed.")
    return output


def restore(source: Path, output: Path) -> Path:
    if not source.is_file():
        raise ValueError("Backup file not found.")
    output = reserve_new_file(output)
    uri = "file:" + quote(str(source.resolve())) + "?mode=ro"
    with sqlite3.connect(uri, uri=True) as original, sqlite3.connect(output) as target:
        if original.execute("PRAGMA integrity_check").fetchone()[0] != "ok":
            raise ValueError("Backup integrity check failed.")
        original.backup(target)
    from sqlalchemy import create_engine

    engine = create_engine(f"sqlite:///{output}")
    try:
        migrate(engine)
        cleanup(engine)
        with engine.begin() as connection:
            connection.execute(delete(LoginSession))
            connection.execute(delete(LoginAttempt))
    finally:
        engine.dispose()
    return output


def daily_maintenance(engine, now: datetime | None = None) -> dict:
    now = now or utcnow()
    result = cleanup(engine, now)
    folder = Path(engine.url.database).parent / "backups"
    output = folder / f"studyspace-{now:%Y-%m-%d}.sqlite"
    if not output.exists():
        backup(engine, output)
    # Only this application's own dated backups are eligible for rotation.
    backups = sorted(folder.glob("studyspace-????-??-??.sqlite"), reverse=True)
    for old in backups[7:]:
        old.unlink()
    return {**result, "backup": str(output)}
