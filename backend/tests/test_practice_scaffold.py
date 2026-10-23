"""Executable practice checks for the implemented diagnostic API only.

These tests do not exercise booking, identity review, or acceptance workflows.
"""

from pathlib import Path

from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import Engine, create_engine

from app.database import get_engine


def test_at_01_health_stays_available_when_database_is_unavailable(
    application: FastAPI, client: TestClient, tmp_path: Path
) -> None:
    """AC-11: liveness and readiness are distinct, and failure hides DB details."""
    private_path = tmp_path / "absent-directory" / "private.db"
    unavailable_engine = create_engine(f"sqlite:///{private_path}")
    application.dependency_overrides[get_engine] = lambda: unavailable_engine
    try:
        health = client.get("/api/v1/health")
        ready = client.get("/api/v1/ready")
        assert health.status_code == 200
        assert health.json() == {"status": "ok", "service": "StudySpace", "version": "0.1.0"}
        assert ready.status_code == 503
        assert ready.json()["database"] == "unavailable"
        assert str(private_path) not in ready.text
    finally:
        application.dependency_overrides.clear()
        unavailable_engine.dispose()


def test_at_02_readiness_recovers_after_database_becomes_available(
    application: FastAPI, client: TestClient, engine: Engine, tmp_path: Path
) -> None:
    """AC-12: a failed readiness check can recover without restarting the API."""
    private_path = tmp_path / "absent-directory" / "private.db"
    unavailable_engine = create_engine(f"sqlite:///{private_path}")
    application.dependency_overrides[get_engine] = lambda: unavailable_engine
    try:
        assert client.get("/api/v1/ready").status_code == 503
        application.dependency_overrides[get_engine] = lambda: engine
        restored = client.get("/api/v1/ready")
        assert restored.status_code == 200
        assert restored.json() == {
            "status": "ok",
            "service": "StudySpace",
            "version": "0.1.0",
            "database": "ok",
        }
    finally:
        application.dependency_overrides.clear()
        unavailable_engine.dispose()


def test_at_03_cors_preflight_allows_only_configured_origin(client: TestClient) -> None:
    """AC-13: browser preflight accepts the local frontend, not another origin."""
    headers = {"Access-Control-Request-Method": "GET"}
    allowed = client.options(
        "/api/v1/ready", headers={**headers, "Origin": "http://localhost:5173"}
    )
    denied = client.options(
        "/api/v1/ready", headers={**headers, "Origin": "https://untrusted.example"}
    )
    assert allowed.status_code == 200
    assert allowed.headers["access-control-allow-origin"] == "http://localhost:5173"
    assert denied.status_code == 400
    assert "access-control-allow-origin" not in denied.headers
