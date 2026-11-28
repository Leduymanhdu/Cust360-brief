"""Runtime configuration for PostgreSQL access, uploads, and the API."""

import os
from collections.abc import Mapping
from pathlib import Path
from urllib.parse import quote_plus

BASE_DIR = Path(__file__).resolve().parent.parent
DEV_DATABASE_URL = (
    "postgresql+psycopg://customer360:local-dev-only@localhost:5432/customer360"
)
DEFAULT_MAX_UPLOAD_BYTES = 10 * 1024 * 1024
DEFAULT_UPLOAD_CHUNK_SIZE = 1024 * 1024


def _positive_int(raw: str | None, default: int) -> int:
    if not raw or not raw.strip():
        return default
    try:
        value = int(raw)
    except ValueError:
        return default
    return value if value > 0 else default


def _boolean(raw: str | None, default: bool = False) -> bool:
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


def app_environment(env: Mapping[str, str] | None = None) -> str:
    """Return the lower-cased deployment environment name."""
    source = os.environ if env is None else env
    return (source.get("APP_ENV") or "development").strip().lower()


def build_database_url(env: Mapping[str, str] | None = None) -> str:
    """Resolve the SQLAlchemy database URL from the environment.

    ``DATABASE_URL`` takes precedence; otherwise the URL is assembled from the
    ``POSTGRES_*`` parts. Outside production a local development default is
    used so the API can start against ``docker compose up postgres``. In
    production a missing configuration is a startup error rather than a silent
    fallback to development credentials.
    """
    source = os.environ if env is None else env
    explicit = (source.get("DATABASE_URL") or "").strip()
    if explicit:
        return explicit

    host = (source.get("POSTGRES_HOST") or "").strip()
    if host:
        user = quote_plus(source.get("POSTGRES_USER", "customer360"))
        password = quote_plus(source.get("POSTGRES_PASSWORD", ""))
        port = _positive_int(source.get("POSTGRES_PORT"), 5432)
        name = quote_plus(source.get("POSTGRES_DB", "customer360"))
        return f"postgresql+psycopg://{user}:{password}@{host}:{port}/{name}"

    if app_environment(source) == "production":
        raise RuntimeError(
            "DATABASE_URL or POSTGRES_HOST must be configured when APP_ENV=production."
        )
    return DEV_DATABASE_URL


APP_ENV = app_environment()
IS_PRODUCTION = APP_ENV == "production"
DATABASE_URL = build_database_url()
SQL_ECHO = _boolean(os.getenv("SQL_ECHO"), default=False)
DB_CONNECT_TIMEOUT = _positive_int(os.getenv("DB_CONNECT_TIMEOUT"), 5)

MAX_UPLOAD_BYTES = _positive_int(
    os.getenv("MAX_UPLOAD_BYTES"),
    DEFAULT_MAX_UPLOAD_BYTES,
)
UPLOAD_CHUNK_SIZE = _positive_int(
    os.getenv("UPLOAD_CHUNK_SIZE"),
    DEFAULT_UPLOAD_CHUNK_SIZE,
)
UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR") or BASE_DIR / "var" / "uploads").resolve()
