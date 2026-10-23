from pathlib import Path

from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, inspect

from app.database import get_engine


def test_health_contract_after_versioned_local_initialization(
    client: TestClient, database_path: Path
) -> None:
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "StudySpace", "version": "0.1.0"}
    assert database_path.exists()


def test_readiness_connects_to_isolated_migrated_database(
    client: TestClient, database_path: Path
) -> None:
    response = client.get("/api/v1/ready")
    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "StudySpace",
        "version": "0.1.0",
        "database": "ok",
    }
    assert database_path.exists()
    engine = create_engine(f"sqlite:///{database_path}")
    try:
        assert {"users", "bookings", "seats", "alembic_version"}.issubset(
            inspect(engine).get_table_names()
        )
    finally:
        engine.dispose()


def test_readiness_database_failure_is_generic(
    application: FastAPI, client: TestClient, tmp_path: Path
) -> None:
    secret_path = tmp_path / "private-db-location" / "unavailable.db"
    failing_engine = create_engine(f"sqlite:///{secret_path}")
    application.dependency_overrides[get_engine] = lambda: failing_engine
    try:
        response = client.get("/api/v1/ready")
        assert response.status_code == 503
        assert response.json() == {
            "status": "unavailable",
            "service": "StudySpace",
            "version": "0.1.0",
            "database": "unavailable",
        }
        assert str(secret_path) not in response.text
        assert "OperationalError" not in response.text
    finally:
        application.dependency_overrides.clear()
        failing_engine.dispose()


def test_cors_allows_local_frontend_and_denies_other_origins(client: TestClient) -> None:
    allowed = client.get("/api/v1/health", headers={"Origin": "http://localhost:5173"})
    denied = client.get("/api/v1/health", headers={"Origin": "https://untrusted.example"})
    assert allowed.headers["access-control-allow-origin"] == "http://localhost:5173"
    assert "access-control-allow-origin" not in denied.headers


def test_openapi_exposes_diagnostics_and_local_auth(client: TestClient) -> None:
    response = client.get("/api/v1/openapi.json")
    assert response.status_code == 200
    assert {"/api/v1/health", "/api/v1/ready", "/api/v1/auth/register", "/api/v1/auth/me"}.issubset(
        response.json()["paths"]
    )
    assert client.get("/api/v1/docs").status_code == 200
