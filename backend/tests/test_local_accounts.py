"""Local-account behavior; no school identity or real personal data.

These tests catch missing auth, plaintext secrets, privilege injection,
case-sensitive duplicates, persistent revoked sessions and cross-site writes.
"""

import hashlib

from fastapi.testclient import TestClient
from sqlalchemy import Engine, text

PASSWORD = "Test-only-password42!"
WRITE = {"X-StudySpace-Request": "1"}


def register(client: TestClient, username: str = "student_a"):
    return client.post(
        "/api/v1/auth/register",
        json={"username": username, "display_name": "演示学生", "password": PASSWORD},
        headers=WRITE,
    )


def login(client: TestClient, username: str = "student_a"):
    return client.post(
        "/api/v1/auth/login",
        json={"username": username, "password": PASSWORD},
        headers=WRITE,
    )


def test_local_registration_needs_no_school_proof_and_hashes_secrets(client, engine: Engine):
    response = register(client)
    assert response.status_code == 201
    body = response.json()
    assert body["username"] == "student_a"
    assert body["role"] == "STUDENT"
    assert body["identity_mode"] == "LOCAL_ONLY"
    assert "password" not in response.text
    with engine.connect() as connection:
        stored = connection.execute(text("SELECT password_hash FROM users")).scalar_one()
    assert stored != PASSWORD
    assert stored.startswith("scrypt$")


def test_login_rotates_private_cookie_and_logout_revokes_it(client, engine: Engine):
    assert register(client).status_code == 201
    assert client.get("/api/v1/auth/me").status_code == 401
    response = login(client)
    assert response.status_code == 200
    token = client.cookies["studyspace_session"]
    cookie = response.headers["set-cookie"].lower()
    assert "httponly" in cookie and "samesite=strict" in cookie
    with engine.connect() as connection:
        hashes = connection.execute(text("SELECT token_hash FROM sessions")).scalars().all()
    assert hashlib.sha256(token.encode()).hexdigest() in hashes
    assert token not in hashes
    assert client.get("/api/v1/auth/me").json()["username"] == "student_a"
    assert client.post("/api/v1/auth/logout", headers=WRITE).status_code == 204
    client.cookies.set("studyspace_session", token)
    assert client.get("/api/v1/auth/me").status_code == 401


def test_casefold_duplicate_and_role_injection_are_rejected(client):
    assert register(client).status_code == 201
    assert register(client, "STUDENT_A").status_code == 409
    attack = client.post(
        "/api/v1/auth/register",
        json={
            "username": "attacker",
            "display_name": "Demo",
            "password": PASSWORD,
            "role": "ADMIN",
        },
        headers=WRITE,
    )
    assert attack.status_code == 422
    assert PASSWORD not in attack.text


def test_disabled_account_and_expired_sessions_cannot_access_private_records(client, engine):
    assert register(client).status_code == 201
    assert login(client).status_code == 200
    with engine.begin() as connection:
        connection.execute(text("UPDATE sessions SET expires_at='2000-01-01 00:00:00'"))
    assert client.get("/api/v1/auth/me").status_code == 401
    assert login(client).status_code == 200
    with engine.begin() as connection:
        connection.execute(text("UPDATE users SET enabled=0 WHERE username='student_a'"))
    assert client.get("/api/v1/auth/me").status_code == 401
    assert login(client).status_code == 401


def test_write_requests_require_same_origin_header(client):
    payload = {"username": "student_a", "display_name": "Demo", "password": PASSWORD}
    assert client.post("/api/v1/auth/register", json=payload).status_code == 403
    cross_site = client.post(
        "/api/v1/auth/register",
        json=payload,
        headers={**WRITE, "Origin": "https://untrusted.example"},
    )
    assert cross_site.status_code == 403
    assert register(client).status_code == 201
    denied = client.post(
        "/api/v1/auth/login", json={"username": "student_a", "password": "wrong"}, headers=WRITE
    )
    assert denied.status_code == 401


def test_empty_malformed_or_unbounded_inputs_do_not_create_accounts(client):
    for username, password in [
        (" ", PASSWORD),
        ("student-b", PASSWORD),
        ("x" * 33, PASSWORD),
        ("valid", "short"),
    ]:
        response = client.post(
            "/api/v1/auth/register",
            json={"username": username, "display_name": "Demo", "password": password},
            headers=WRITE,
        )
        assert response.status_code == 422
        assert password not in response.text


def test_password_spaces_are_significant_and_login_throttling_persists(client):
    password = "  Test-only-password42!  "
    assert (
        client.post(
            "/api/v1/auth/register",
            json={"username": "spaced", "display_name": "Demo", "password": password},
            headers=WRITE,
        ).status_code
        == 201
    )
    assert (
        client.post(
            "/api/v1/auth/login",
            json={"username": "spaced", "password": password.strip()},
            headers=WRITE,
        ).status_code
        == 401
    )
    assert (
        client.post(
            "/api/v1/auth/login", json={"username": "spaced", "password": password}, headers=WRITE
        ).status_code
        == 200
    )
    for _ in range(5):
        assert (
            client.post(
                "/api/v1/auth/login",
                json={"username": "missing", "password": PASSWORD},
                headers=WRITE,
            ).status_code
            == 401
        )
    assert (
        client.post(
            "/api/v1/auth/login", json={"username": "missing", "password": PASSWORD}, headers=WRITE
        ).status_code
        == 429
    )
