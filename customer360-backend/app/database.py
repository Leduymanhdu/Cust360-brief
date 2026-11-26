"""SQLAlchemy database engine, session factory, and table creation."""

from collections.abc import Iterator
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session

from app import config

# Connect args for SQLite support
connect_args = {}
if config.DATABASE_URL.startswith("sqlite"):
    connect_args["check_same_thread"] = False

engine = create_engine(
    config.DATABASE_URL,
    echo=config.SQL_ECHO,
    connect_args=connect_args,
    pool_pre_ping=True if not config.DATABASE_URL.startswith("sqlite") else False,
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
Base = declarative_base()


def get_db() -> Iterator[Session]:
    """Yield a database session per request and close it afterwards."""
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


def init_db() -> None:
    """Create all tables and seed initial users and accounts if empty."""
    Base.metadata.create_all(bind=engine)
    from app.services.db_seeder import seed_initial_data
    with SessionLocal() as db:
        seed_initial_data(db)
