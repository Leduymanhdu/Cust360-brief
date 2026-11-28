"""SQLAlchemy engine, session factory, and database connectivity check."""

from collections.abc import Iterator

from sqlalchemy import Engine, create_engine, text
from sqlalchemy.orm import Session, sessionmaker

from app import config

engine: Engine = create_engine(
    config.DATABASE_URL,
    echo=config.SQL_ECHO,
    pool_pre_ping=True,
    connect_args={"connect_timeout": config.DB_CONNECT_TIMEOUT},
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def get_db() -> Iterator[Session]:
    """Yield a database session per request and close it afterwards."""
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


def ping_database() -> None:
    """Run a trivial query so callers can detect an unreachable database."""
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))
