"""Run versioned SQLite migrations against the configured engine."""

from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import Engine


def migrate(engine: Engine, revision: str = "head") -> None:
    config = Config()
    config.set_main_option(
        "script_location", str(Path(__file__).resolve().parents[1] / "migrations")
    )
    with engine.connect() as connection:
        if engine.dialect.name == "sqlite":
            connection.exec_driver_sql("PRAGMA journal_mode=WAL")
            connection.commit()
        config.attributes["connection"] = connection
        if revision == "base":
            command.downgrade(config, "base")
        else:
            command.upgrade(config, revision)
