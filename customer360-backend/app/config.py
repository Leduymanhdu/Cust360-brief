"""Runtime configuration for imported file uploads and storage."""

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DEFAULT_MAX_UPLOAD_BYTES = 10 * 1024 * 1024
DEFAULT_UPLOAD_CHUNK_SIZE = 1024 * 1024


def _positive_int_from_env(name: str, default: int) -> int:
    raw = os.getenv(name)
    if not raw or not raw.strip():
        return default
    try:
        value = int(raw)
    except ValueError:
        return default
    return value if value > 0 else default


MAX_UPLOAD_BYTES = _positive_int_from_env(
    "MAX_UPLOAD_BYTES",
    DEFAULT_MAX_UPLOAD_BYTES,
)
UPLOAD_CHUNK_SIZE = _positive_int_from_env(
    "UPLOAD_CHUNK_SIZE",
    DEFAULT_UPLOAD_CHUNK_SIZE,
)
UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR") or BASE_DIR / "var" / "uploads").resolve()
