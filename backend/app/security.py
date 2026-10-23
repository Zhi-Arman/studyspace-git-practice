"""Opaque, revocable local sessions and salted scrypt passwords."""

import hashlib
import hmac
import secrets
from datetime import UTC, datetime

from fastapi import Request
from sqlalchemy.orm import Session

from app.errors import fail
from app.models import AuditEvent, LoginSession, User

COOKIE = "studyspace_session"


def utcnow() -> datetime:
    return datetime.now(UTC).replace(tzinfo=None)


def digest_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    key = hashlib.scrypt(password.encode(), salt=bytes.fromhex(salt), n=16384, r=8, p=1)
    return f"scrypt$16384$8$1${salt}${key.hex()}"


def verify_password(password: str, stored: str) -> bool:
    try:
        kind, n, r, p, salt, expected = stored.split("$")
        if (kind, n, r, p) != ("scrypt", "16384", "8", "1"):
            return False
        actual = hashlib.scrypt(password.encode(), salt=bytes.fromhex(salt), n=16384, r=8, p=1)
        return hmac.compare_digest(actual.hex(), expected)
    except (ValueError, TypeError):
        return False


def request_user(request: Request, db: Session, *, admin: bool = False) -> User:
    token = request.cookies.get(COOKIE, "")
    session = db.get(LoginSession, digest_token(token)) if token else None
    if session is None or session.expires_at <= utcnow():
        fail(401, "AUTH_REQUIRED", "Sign in to continue.")
    user = db.get(User, session.user_id)
    if user is None or not user.enabled:
        fail(401, "AUTH_REQUIRED", "Sign in to continue.")
    if admin and user.role != "ADMIN":
        fail(403, "ADMIN_REQUIRED", "Administrator access is required.")
    return user


def user_view(user: User) -> dict:
    return {
        "id": user.id,
        "username": user.username,
        "display_name": user.display_name,
        "role": user.role,
        "enabled": user.enabled,
        "identity_mode": "LOCAL_ONLY",
    }


def audit(db: Session, actor_id: int | None, action: str, target_type: str, target_id: int):
    db.add(
        AuditEvent(
            actor_id=actor_id,
            action=action,
            target_type=target_type,
            target_id=target_id,
            created_at=utcnow(),
        )
    )
