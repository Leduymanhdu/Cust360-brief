"""Import orchestration: upload validation, storage, and job status tracking."""

import csv
import io
from datetime import datetime, timezone
from uuid import UUID, uuid4

from fastapi import BackgroundTasks, HTTPException, UploadFile, status

from app import config
from app.schemas import (
    ImportedFileMetadata,
    ImportFileKind,
    ImportJobResponse,
    ImportJobStatus,
)
from app.services.storage import (
    FileTooLargeError,
    StorageError,
    StoredFile,
    delete_stored_file,
    read_checksum,
    store_upload,
)

CSV_CONTENT_TYPES = {
    "text/csv",
    "application/csv",
    "application/vnd.ms-excel",
    "application/octet-stream",
}
PDF_CONTENT_TYPES = {
    "application/pdf",
    "application/octet-stream",
}
KIND_EXTENSIONS = {
    ImportFileKind.CSV: ".csv",
    ImportFileKind.PDF: ".pdf",
}
KIND_CONTENT_TYPES = {
    ImportFileKind.CSV: CSV_CONTENT_TYPES,
    ImportFileKind.PDF: PDF_CONTENT_TYPES,
}
INJECTION_TERMS = (
    "ignore previous instructions",
    "system prompt",
    "reveal your instructions",
)

IMPORT_JOBS: dict[UUID, ImportJobResponse] = {}


class ImportValidationError(ValueError):
    """Raised when an uploaded file fails content validation."""


class ImportProcessingError(RuntimeError):
    """Raised when a stored file cannot be turned into an import result."""


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _validate_declared_format(file: UploadFile, kind: ImportFileKind) -> None:
    """Reject files whose extension or content type does not match the endpoint."""
    expected_extension = KIND_EXTENSIONS[kind]
    if not file.filename or not file.filename.lower().endswith(expected_extension):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"A {expected_extension} file is required.",
        )
    if file.content_type not in KIND_CONTENT_TYPES[kind]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported file content type.",
        )


def _inspect_stored_file(
    stored: StoredFile,
    kind: ImportFileKind,
) -> tuple[int, list[str]]:
    """Validate stored content and return the record count plus any warnings."""
    try:
        content = stored.path.read_bytes()
    except OSError as exc:
        raise ImportValidationError("Không đọc được file vừa lưu.") from exc

    if kind is ImportFileKind.PDF:
        if not content.startswith(b"%PDF-"):
            raise ImportValidationError("File không có chữ ký PDF hợp lệ.")
        decoded = content.decode("latin-1", errors="ignore").casefold()
        flagged = any(term in decoded for term in INJECTION_TERMS)
        warnings = (
            ["PDF được đánh dấu để kiểm tra cách ly (nghi vấn prompt injection)."]
            if flagged
            else []
        )
        return 1, warnings

    try:
        rows = list(csv.reader(io.StringIO(content.decode("utf-8-sig"))))
    except (UnicodeDecodeError, csv.Error) as exc:
        raise ImportValidationError("CSV phải là văn bản UTF-8 hợp lệ.") from exc
    if not rows:
        raise ImportValidationError("File CSV rỗng.")
    return max(len(rows) - 1, 0), []


def _update_job(job: ImportJobResponse, **changes: object) -> ImportJobResponse:
    updated = job.model_copy(update={"updated_at": _now(), **changes})
    IMPORT_JOBS[updated.job_id] = updated
    return updated


def get_import_job(job_id: UUID) -> ImportJobResponse | None:
    return IMPORT_JOBS.get(job_id)


def verify_stored_file(job: ImportJobResponse) -> None:
    """Confirm the stored file still exists and matches its upload checksum."""
    path = config.UPLOAD_DIR / job.file.storage_path
    if not path.is_file():
        raise ImportProcessingError("File lưu trữ không còn tồn tại.")
    if read_checksum(path) != job.file.checksum_sha256:
        raise ImportProcessingError("Checksum file lưu trữ không khớp.")


def process_import(job_id: UUID) -> None:
    """Move a queued import job to COMPLETED, or to FAILED on error."""
    job = IMPORT_JOBS.get(job_id)
    if job is None:
        return
    job = _update_job(job, status=ImportJobStatus.PROCESSING)
    try:
        verify_stored_file(job)
    except (ImportProcessingError, OSError) as exc:
        _update_job(
            job,
            status=ImportJobStatus.FAILED,
            error=str(exc),
            message="Import thất bại.",
        )
        return
    _update_job(
        job,
        status=ImportJobStatus.COMPLETED,
        completed_at=_now(),
        message=(
            f"Đã nhận {job.records_received} bản ghi; lưu trữ và xử lý nền được mô phỏng."
        ),
    )


async def start_import(
    file: UploadFile,
    kind: ImportFileKind,
    background_tasks: BackgroundTasks,
) -> ImportJobResponse:
    """Validate, store, and queue one CSV/PDF upload as an import job."""
    _validate_declared_format(file, kind)
    try:
        stored = await store_upload(
            file,
            upload_dir=config.UPLOAD_DIR,
            max_bytes=config.MAX_UPLOAD_BYTES,
            chunk_size=config.UPLOAD_CHUNK_SIZE,
            subdir=kind.value.lower(),
        )
    except FileTooLargeError as exc:
        raise HTTPException(
            status_code=status.HTTP_413_CONTENT_TOO_LARGE,
            detail=f"File vượt giới hạn {config.MAX_UPLOAD_BYTES} bytes.",
        ) from exc
    except StorageError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Không thể lưu file lên hệ thống lưu trữ.",
        ) from exc

    try:
        records_received, warnings = _inspect_stored_file(stored, kind)
    except ImportValidationError as exc:
        delete_stored_file(stored.path)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    now = _now()
    job = ImportJobResponse(
        job_id=uuid4(),
        status=ImportJobStatus.PENDING,
        file=ImportedFileMetadata(
            file_name=file.filename or f"upload{stored.path.suffix}",
            kind=kind,
            content_type=file.content_type or "application/octet-stream",
            size_bytes=stored.size_bytes,
            checksum_sha256=stored.checksum_sha256,
            storage_path=stored.relative_path,
        ),
        records_received=records_received,
        warnings=warnings,
        message="Đã nhận file; import đang chờ xử lý.",
        created_at=now,
        updated_at=now,
    )
    IMPORT_JOBS[job.job_id] = job
    background_tasks.add_task(process_import, job.job_id)
    return job
