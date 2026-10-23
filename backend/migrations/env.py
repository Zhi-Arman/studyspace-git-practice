"""Migrations use an explicitly supplied engine, never credentials in an ini file."""

import app.models  # noqa: F401
from alembic import context
from app.database import Base

connection = context.config.attributes["connection"]
context.configure(connection=connection, target_metadata=Base.metadata, render_as_batch=True)
with context.begin_transaction():
    context.run_migrations()
