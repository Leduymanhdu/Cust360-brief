import csv
import io
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from psycopg import Connection

from app.database import get_db_connection
from app.schemas import (
    ErrorResponse,
    ImportJobResponse,
    RevokeAccessRequest,
    RevokeAccessResponse,
)
from app.security import require_admin

router = APIRouter(prefix="/admin", tags=["Administration"])
MAX_UPLOAD_BYTES = 10 * 1024 * 1024
CSV_CONTENT_TYPES = {
    "text/csv",
    "application/csv",
    "application/vnd.ms-excel",
    "application/octet-stream",
}
INJECTION_TERMS = (
    "ignore previous instructions",
    "system prompt",
    "reveal your instructions",
)


async def _read_upload(file: UploadFile, allowed_types: set[str]) -> bytes:
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail="Unsupported file content type.",
        )
    content = await file.read(MAX_UPLOAD_BYTES + 1)
    if len(content) > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=413, detail="File exceeds the 10 MiB limit.")
    return content


@router.post(
    "/import/csv",
    response_model=ImportJobResponse,
    summary="Upload a CSV file for asynchronous import",
    responses={
        400: {"model": ErrorResponse, "description": "Unsupported or invalid CSV file."},
        401: {"model": ErrorResponse, "description": "Authentication required."},
        403: {"model": ErrorResponse, "description": "Administrator role required."},
        413: {"model": ErrorResponse, "description": "File exceeds the 10 MiB limit."},
    },
)
async def import_csv(
    file: UploadFile = File(..., description="UTF-8 CSV file; maximum size 10 MiB."),
    _admin: dict = Depends(require_admin),
) -> ImportJobResponse:
    """Validate a CSV payload and return a mock processing job."""
    if not file.filename or not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="A .csv file is required.")
    content = await _read_upload(file, CSV_CONTENT_TYPES)
    try:
        text = content.decode("utf-8-sig")
        rows = list(csv.reader(io.StringIO(text)))
    except (UnicodeDecodeError, csv.Error) as exc:
        raise HTTPException(status_code=400, detail="CSV must be valid UTF-8.") from exc
    if not rows:
        raise HTTPException(status_code=400, detail="CSV file is empty.")
    return ImportJobResponse(
        job_id=uuid4(),
        records_received=max(len(rows) - 1, 0),
        message="CSV accepted. Persistence and background processing are mocked.",
    )


@router.post(
    "/import/pdf",
    response_model=ImportJobResponse,
    summary="Upload a PDF file for text extraction and safety scanning",
    responses={
        400: {"model": ErrorResponse, "description": "Unsupported or invalid PDF file."},
        401: {"model": ErrorResponse, "description": "Authentication required."},
        403: {"model": ErrorResponse, "description": "Administrator role required."},
        413: {"model": ErrorResponse, "description": "File exceeds the 10 MiB limit."},
    },
)
async def import_pdf(
    file: UploadFile = File(..., description="PDF file; maximum size 10 MiB."),
    _admin: dict = Depends(require_admin),
) -> ImportJobResponse:
    """Check PDF signature and flag obvious prompt-injection language."""
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="A .pdf file is required.")
    content = await _read_upload(file, {"application/pdf"})
    if not content.startswith(b"%PDF-"):
        raise HTTPException(status_code=400, detail="File does not have a valid PDF signature.")
    decoded = content.decode("latin-1", errors="ignore").casefold()
    flagged = any(term in decoded for term in INJECTION_TERMS)
    return ImportJobResponse(
        job_id=uuid4(),
        records_received=1,
        message=(
            "PDF accepted and flagged for quarantine review."
            if flagged
            else "PDF accepted. Text extraction and storage are mocked."
        ),
    )


@router.post(
    "/users/{user_id}/revoke-access",
    response_model=RevokeAccessResponse,
    summary="Revoke one user's access to an account",
    responses={
        401: {"model": ErrorResponse, "description": "Authentication required."},
        403: {"model": ErrorResponse, "description": "Administrator role required."},
        404: {"model": ErrorResponse, "description": "User or account not found."},
        500: {"model": ErrorResponse, "description": "Database operation failed."},
        503: {"model": ErrorResponse, "description": "Database is unavailable."},
    },
)
def revoke_access(
    user_id: UUID,
    payload: RevokeAccessRequest,
    admin: dict = Depends(require_admin),
    connection: Connection = Depends(get_db_connection),
) -> RevokeAccessResponse:
    """Revoke a user's account scope in PostgreSQL."""
    if user_id == admin["user"].id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An administrator cannot revoke their own access.",
        )

    with connection.transaction():
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1 FROM users WHERE id = %s", (user_id,))
            user_exists = cursor.fetchone() is not None
            cursor.execute(
                "SELECT 1 FROM accounts WHERE id = %s",
                (payload.account_id,),
            )
            account_exists = cursor.fetchone() is not None
            if not user_exists or not account_exists:
                raise HTTPException(
                    status_code=404,
                    detail="User or account not found.",
                )
            cursor.execute(
                """
                DELETE FROM user_account_access
                WHERE user_id = %s AND account_id = %s
                """,
                (user_id, payload.account_id),
            )
            was_granted = cursor.rowcount > 0

    return RevokeAccessResponse(
        user_id=user_id,
        account_id=payload.account_id,
        revoked=was_granted,
        cache_cleared=False,
        message=f"Access revocation recorded. Reason: {payload.reason}",
    )
