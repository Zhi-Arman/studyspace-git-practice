from pathlib import Path

import pytest
from sqlalchemy.engine import make_url

from app.config import DEFAULT_DATABASE_PATH, Settings


def test_default_database_is_absolute_and_independent_of_cwd(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    first = Settings(_env_file=None)
    monkeypatch.chdir(tmp_path)
    second = Settings(_env_file=None)
    database = make_url(second.database_url).database
    assert database is not None
    assert Path(database).is_absolute()
    assert Path(database) == DEFAULT_DATABASE_PATH
    assert second.database_url == first.database_url


def test_settings_read_absolute_env_file_and_json_cors(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    env_directory = tmp_path / "project"
    env_directory.mkdir()
    env_path = env_directory / ".env"
    database_path = env_directory / "custom.db"
    env_path.write_text(
        f"APP_ENV=test\nDATABASE_URL=sqlite:///{database_path}\n"
        'CORS_ORIGINS=["http://127.0.0.1:5173"]\n',
        encoding="utf-8",
    )
    monkeypatch.chdir(tmp_path)
    settings = Settings(_env_file=env_path)
    assert settings.app_env == "test"
    assert settings.database_url == f"sqlite:///{database_path}"
    assert settings.cors_origins == ["http://127.0.0.1:5173"]


def test_environment_overrides_env_file(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    env_path = tmp_path / ".env"
    env_path.write_text("APP_ENV=development\n", encoding="utf-8")
    monkeypatch.setenv("APP_ENV", "test")
    assert Settings(_env_file=env_path).app_env == "test"
