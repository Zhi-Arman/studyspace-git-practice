from collections.abc import Iterator
from pathlib import Path

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import Engine

from app.config import Settings
from app.database import create_db_engine
from app.main import create_app


@pytest.fixture(autouse=True)
def isolate_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    for key in ["APP_ENV", "DATABASE_URL", "CORS_ORIGINS"]:
        monkeypatch.delenv(key, raising=False)


@pytest.fixture
def database_path(tmp_path: Path) -> Path:
    return tmp_path / "test-studyspace.db"


@pytest.fixture
def engine(database_path: Path) -> Iterator[Engine]:
    settings = Settings(_env_file=None, app_env="test", database_url=f"sqlite:///{database_path}")
    database_engine = create_db_engine(settings)
    yield database_engine
    database_engine.dispose()


@pytest.fixture
def application(engine: Engine, database_path: Path) -> FastAPI:
    settings = Settings(_env_file=None, app_env="test", database_url=f"sqlite:///{database_path}")
    return create_app(settings=settings, engine=engine)


@pytest.fixture
def client(application: FastAPI) -> Iterator[TestClient]:
    with TestClient(application) as test_client:
        yield test_client
