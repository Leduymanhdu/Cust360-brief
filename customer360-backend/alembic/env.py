"""Alembic environment driven by the application's environment variables."""

from logging.config import fileConfig

from alembic import context
from sqlalchemy import create_engine, pool

from app import config as app_config

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Schema changes are declared with explicit operations, so autogenerate has no
# metadata to compare against yet. Point this at the ORM metadata once the
# domain models replace the current in-memory mock data.
target_metadata = None


def run_migrations_offline() -> None:
    """Emit SQL to stdout without connecting to the database."""
    context.configure(
        url=app_config.DATABASE_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Apply migrations against the database in DATABASE_URL."""
    connectable = create_engine(app_config.DATABASE_URL, poolclass=pool.NullPool)
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
