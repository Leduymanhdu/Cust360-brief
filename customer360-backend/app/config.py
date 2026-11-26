"""Runtime configuration for database, security, JWT and API."""

import os
from collections.abc import Mapping
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# Database configuration: defaults to SQLite for local self-contained operation,
# or PostgreSQL when configured via DATABASE_URL or POSTGRES_*.
def build_database_url(env: Mapping[str, str] | None = None) -> str:
    source = os.environ if env is None else env
    explicit = (source.get("DATABASE_URL") or "").strip()
    if explicit:
        return explicit

    host = (source.get("POSTGRES_HOST") or "").strip()
    if host:
        from urllib.parse import quote_plus
        user = quote_plus(source.get("POSTGRES_USER", "customer360"))
        password = quote_plus(source.get("POSTGRES_PASSWORD", ""))
        port = int(source.get("POSTGRES_PORT", "5432"))
        name = quote_plus(source.get("POSTGRES_DB", "customer360"))
        return f"postgresql+psycopg://{user}:{password}@{host}:{port}/{name}"

    # Default to sqlite file in backend directory for zero-dependency local execution
    sqlite_path = BASE_DIR / "customer360.db"
    return f"sqlite:///{sqlite_path.as_posix()}"


DATABASE_URL = build_database_url()
SQL_ECHO = os.getenv("SQL_ECHO", "false").strip().lower() in {"1", "true", "yes"}

# Security & JWT configuration
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "super-secret-key-change-in-production-customer360-jwt-token")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "15"))  # 900 seconds
PASSWORD_HASH_ALGORITHM = os.getenv("PASSWORD_HASH_ALGORITHM", "bcrypt")  # "bcrypt" or "argon2"

# Login security
MAX_FAILED_LOGIN_ATTEMPTS = int(os.getenv("MAX_FAILED_LOGIN_ATTEMPTS", "5"))
ACCOUNT_LOCK_MINUTES = int(os.getenv("ACCOUNT_LOCK_MINUTES", "30"))
