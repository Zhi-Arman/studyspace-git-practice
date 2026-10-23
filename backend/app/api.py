"""Local account API. Business routers are registered in main.py."""

import secrets
from datetime import timedelta

from fastapi import APIRouter, Request, Response
from fastapi.responses import JSONResponse
from sqlalchemy import delete, select

from app.database import DbSession, write_session
from app.errors import fail
from app.models import LoginAttempt, LoginSession, User
from app.schemas import Login, Register
from app.security import (
    COOKIE,
    audit,
    digest_token,
    hash_password,
    request_user,
    user_view,
    utcnow,
    verify_password,
)

router = APIRouter(prefix="/api/v1/auth", tags=["Local accounts"])


@router.post("/register", status_code=201)
def register(payload: Register, request: Request):
    with write_session(request) as db:
        if db.scalar(select(User.id).where(User.username == payload.username)):
            fail(409, "USERNAME_TAKEN", "This username is already in use.")
        user = User(
            username=payload.username,
            display_name=payload.display_name,
            password_hash=hash_password(payload.password),
            role="STUDENT",
            enabled=True,
            created_at=utcnow(),
        )
        db.add(user)
        db.flush()
        audit(db, user.id, "REGISTER", "user", user.id)
        return user_view(user)


@router.post("/login")
def login(payload: Login, request: Request, response: Response):
    with write_session(request) as db:
        now = utcnow()
        key = digest_token(payload.username.lower())
        attempt = db.get(LoginAttempt, key)
        if attempt and attempt.window_start > now - timedelta(minutes=5) and attempt.failures >= 5:
            fail(429, "LOGIN_THROTTLED", "Too many attempts. Try again in five minutes.")
        user = db.scalar(select(User).where(User.username == payload.username.lower()))
        if (
            user is None
            or not user.enabled
            or not verify_password(payload.password, user.password_hash)
        ):
            if attempt is None:
                attempt = LoginAttempt(key=key, failures=0, window_start=now)
                db.add(attempt)
            if attempt.window_start <= now - timedelta(minutes=5):
                attempt.failures, attempt.window_start = 0, now
            attempt.failures += 1
            # Return after committing the attempt; throwing here would roll it back.
            return JSONResponse(
                status_code=401,
                content={
                    "error": {
                        "code": "INVALID_CREDENTIALS",
                        "message": "Username or password is incorrect.",
                    }
                },
            )
        if attempt:
            db.delete(attempt)
        current = request.cookies.get(COOKIE)
        if current:
            db.execute(delete(LoginSession).where(LoginSession.token_hash == digest_token(current)))
        db.execute(delete(LoginSession).where(LoginSession.expires_at <= now))
        token = secrets.token_urlsafe(32)
        db.add(
            LoginSession(
                token_hash=digest_token(token),
                user_id=user.id,
                created_at=now,
                expires_at=now + timedelta(hours=12),
            )
        )
        audit(db, user.id, "LOGIN", "user", user.id)
        response.set_cookie(
            COOKIE, token, max_age=43200, httponly=True, secure=False, samesite="strict", path="/"
        )
        return user_view(user)


@router.get("/me")
def me(request: Request, db: DbSession):
    return user_view(request_user(request, db))


@router.post("/logout", status_code=204)
def logout(request: Request, response: Response):
    with write_session(request) as db:
        token = request.cookies.get(COOKIE)
        if token:
            db.execute(delete(LoginSession).where(LoginSession.token_hash == digest_token(token)))
    response.delete_cookie(COOKIE, path="/", samesite="strict", httponly=True)
