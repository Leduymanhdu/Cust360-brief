"""Filesystem storage for uploaded CSV and PDF files."""

import hashlib
from dataclasses import dataclass
from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile

CHECKSUM_CHUNK_SIZE = 1024 * 1024


class StorageError(RuntimeError):
    """Raised when an upload cannot be persisted to or removed from disk."""


class FileTooLargeError(StorageError):
    """Raised when an upload exceeds the configured size limit."""


@dataclass(frozen=True)
class StoredFile:
    path: Path
    relative_path: str
    size_bytes: int
    checksum_sha256: str


def read_checksum(path: Path) -> str:
    """Return the SHA-256 checksum of a file on disk."""
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(CHECKSUM_CHUNK_SIZE), b""):
            digest.update(chunk)
    return digest.hexdigest()


def delete_stored_file(path: Path) -> None:
    """Remove a stored file, ignoring filesystem errors during cleanup."""
    try:
        path.unlink(missing_ok=True)
    except OSError:
        pass


async def store_upload(
    file: UploadFile,
    *,
    upload_dir: Path,
    max_bytes: int,
    chunk_size: int,
    subdir: str,
) -> StoredFile:
    """Stream an upload to disk, enforcing the configured size limit."""
    root = Path(upload_dir).resolve()
    directory = root / subdir
    try:
        directory.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        raise StorageError(f"Không thể tạo thư mục lưu trữ: {exc}") from exc

    suffix = Path(file.filename or "").suffix.lower()
    destination = directory / f"{uuid4().hex}{suffix}"
    digest = hashlib.sha256()
    size_bytes = 0
    try:
        with destination.open("wb") as handle:
            while chunk := await file.read(chunk_size):
                size_bytes += len(chunk)
                if size_bytes > max_bytes:
                    raise FileTooLargeError(
                        f"File vượt giới hạn {max_bytes} bytes."
                    )
                handle.write(chunk)
                digest.update(chunk)
    except FileTooLargeError:
        delete_stored_file(destination)
        raise
    except OSError as exc:
        delete_stored_file(destination)
        raise StorageError(f"Không thể ghi file lên đĩa: {exc}") from exc

    return StoredFile(
        path=destination,
        relative_path=destination.relative_to(root).as_posix(),
        size_bytes=size_bytes,
        checksum_sha256=digest.hexdigest(),
    )
