from uuid import UUID

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    File,
    HTTPException,
    UploadFile,
    status,
)

from app.mock_data import ACCOUNTS, DEMO_USERS
from app.schemas import (
    ErrorResponse,
    ImportFileKind,
    ImportJobResponse,
    RevokeAccessRequest,
    RevokeAccessResponse,
)
from app.security import require_admin
from app.services import import_service

router = APIRouter(prefix="/admin", tags=["Administration"])


@router.post(
    "/import/csv",
    response_model=ImportJobResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Upload a CSV file and queue an import job",
    responses={
        400: {"model": ErrorResponse, "description": "Unsupported or invalid CSV file."},
        401: {"model": ErrorResponse, "description": "Authentication required."},
        403: {"model": ErrorResponse, "description": "Administrator role required."},
        413: {"model": ErrorResponse, "description": "File exceeds the configured limit."},
        500: {"model": ErrorResponse, "description": "Stored file could not be written."},
    },
)
async def import_csv(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(..., description="UTF-8 CSV file within the configured size limit."),
    _admin: dict = Depends(require_admin),
) -> ImportJobResponse:
    """Validate and store a CSV upload, then queue it for import processing."""
    return await import_service.start_import(file, ImportFileKind.CSV, background_tasks)


@router.post(
    "/import/pdf",
    response_model=ImportJobResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Upload a PDF file and queue an import job",
    responses={
        400: {"model": ErrorResponse, "description": "Unsupported or invalid PDF file."},
        401: {"model": ErrorResponse, "description": "Authentication required."},
        403: {"model": ErrorResponse, "description": "Administrator role required."},
        413: {"model": ErrorResponse, "description": "File exceeds the configured limit."},
        500: {"model": ErrorResponse, "description": "Stored file could not be written."},
    },
)
async def import_pdf(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(..., description="PDF file within the configured size limit."),
    _admin: dict = Depends(require_admin),
) -> ImportJobResponse:
    """Validate and store a PDF upload, then queue it for import processing."""
    return await import_service.start_import(file, ImportFileKind.PDF, background_tasks)


@router.get(
    "/imports/{job_id}",
    response_model=ImportJobResponse,
    summary="Get the status and metadata of an import job",
    responses={
        401: {"model": ErrorResponse, "description": "Authentication required."},
        403: {"model": ErrorResponse, "description": "Administrator role required."},
        404: {"model": ErrorResponse, "description": "Import job not found."},
    },
)
def get_import_job(
    job_id: UUID,
    _admin: dict = Depends(require_admin),
) -> ImportJobResponse:
    """Return the current import status and stored-file metadata for one job."""
    job = import_service.get_import_job(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Import job not found.")
    return job


@router.post(
    "/users/{user_id}/revoke-access",
    response_model=RevokeAccessResponse,
    summary="Revoke one user's access to an account",
    responses={
        401: {"model": ErrorResponse, "description": "Authentication required."},
        403: {"model": ErrorResponse, "description": "Administrator role required."},
        404: {"model": ErrorResponse, "description": "User or account not found."},
    },
)
def revoke_access(
    user_id: UUID,
    payload: RevokeAccessRequest,
    admin: dict = Depends(require_admin),
) -> RevokeAccessResponse:
    """Revoke a seeded user's account scope (mock cache invalidation)."""
    target = next(
        (account for account in DEMO_USERS.values() if account["user"].id == user_id),
        None,
    )
    if target is None or not any(
        account.id == payload.account_id for account in ACCOUNTS
    ):
        raise HTTPException(status_code=404, detail="User or account not found.")
    if target is admin:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The demo administrator cannot revoke their own access.",
        )
    was_granted = payload.account_id in target["account_ids"]
    target["account_ids"].discard(payload.account_id)
    return RevokeAccessResponse(
        user_id=user_id,
        account_id=payload.account_id,
        revoked=was_granted,
        cache_cleared=True,
        message=f"Access revocation recorded. Reason: {payload.reason}",
    )
