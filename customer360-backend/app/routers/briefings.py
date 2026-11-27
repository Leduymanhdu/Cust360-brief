from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Response, status
from psycopg import Connection

from app.database import get_db_connection
from app.services.briefing_service import create_briefing
from app.schemas import (
    BriefingAcceptedResponse,
    BriefingCitationsResponse,
    BriefingGenerationRequest,
    BriefingResponse,
    ErrorResponse,
)
from app.security import check_account_access, get_current_user

router = APIRouter(prefix="/briefings", tags=["Briefings"])


@router.post(
    "/generate",
    response_model=BriefingAcceptedResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Start generation of a six-section account briefing",
    responses={
        403: {"model": ErrorResponse, "description": "ACC-002 Account access denied."},
        404: {"model": ErrorResponse, "description": "ACC-001 Account or site not found."},
        500: {"model": ErrorResponse, "description": "Database operation failed."},
        503: {"model": ErrorResponse, "description": "Database is unavailable."},
    },
)
def generate_briefing(
    payload: BriefingGenerationRequest,
    user: dict = Depends(get_current_user),
    connection: Connection = Depends(get_db_connection),
) -> BriefingAcceptedResponse:
    """Create and persist a deterministic briefing from database evidence."""
    with connection.cursor() as cursor:
        cursor.execute("SELECT 1 FROM accounts WHERE id = %s", (payload.account_id,))
        account_exists = cursor.fetchone() is not None
    if not account_exists:
        raise HTTPException(status_code=404, detail="Account not found.")

    check_account_access(user, payload.account_id)
    try:
        briefing_id = create_briefing(
            connection,
            payload.account_id,
            payload.site_id,
            user["user"].id,
        )
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return BriefingAcceptedResponse(
        briefing_id=briefing_id,
        status="GENERATING",
        message="Briefing generation accepted; retrieve it using briefing_id.",
    )


@router.get(
    "/{briefing_id}",
    response_model=BriefingResponse,
    summary="Get a briefing and all six sections",
    responses={
        403: {"model": ErrorResponse, "description": "ACC-002 Account access denied."},
        404: {"model": ErrorResponse, "description": "BRF-001 Briefing not found."},
        500: {"model": ErrorResponse, "description": "Database query failed."},
        503: {"model": ErrorResponse, "description": "Database is unavailable."},
    },
)
def get_briefing(
    briefing_id: UUID,
    user: dict = Depends(get_current_user),
    connection: Connection = Depends(get_db_connection),
) -> BriefingResponse:
    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT id, account_id, site_id, briefing_status, is_stale, sections,
                   validation_status, created_at, completed_at
            FROM briefings
            WHERE id = %s
            """,
            (briefing_id,),
        )
        row = cursor.fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="Briefing not found.")
    check_account_access(user, row["account_id"])
    return BriefingResponse(
        briefing_id=row["id"],
        account_id=row["account_id"],
        site_id=row["site_id"],
        status=row["briefing_status"],
        is_stale=row["is_stale"],
        sections=row["sections"],
        validation_status=row["validation_status"],
        created_at=row["created_at"],
        completed_at=row["completed_at"],
    )


@router.get(
    "/{briefing_id}/citations",
    response_model=BriefingCitationsResponse,
    summary="List source citations for a briefing",
    responses={
        403: {"model": ErrorResponse, "description": "ACC-002 Account access denied."},
        404: {"model": ErrorResponse, "description": "BRF-001 Briefing not found."},
        500: {"model": ErrorResponse, "description": "Database query failed."},
        503: {"model": ErrorResponse, "description": "Database is unavailable."},
    },
)
def get_briefing_citations(
    briefing_id: UUID,
    user: dict = Depends(get_current_user),
    connection: Connection = Depends(get_db_connection),
) -> BriefingCitationsResponse:
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT account_id FROM briefings WHERE id = %s",
            (briefing_id,),
        )
        briefing = cursor.fetchone()
    if briefing is None:
        raise HTTPException(status_code=404, detail="Briefing not found.")
    check_account_access(user, briefing["account_id"])

    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT c.citation_number, c.claim_text, c.source_type,
                   COALESCE(c.pdf_text_id, c.commercial_record_id) AS source_id,
                   p.page_number,
                   COALESCE(c.source_excerpt, p.extracted_text) AS source_excerpt,
                   c.validation_status
            FROM citations AS c
            LEFT JOIN pdf_text AS p ON p.id = c.pdf_text_id
            LEFT JOIN commercial_records AS cr ON cr.id = c.commercial_record_id
            WHERE c.briefing_id = %s
              AND (
                  (
                      c.source_type = 'PDF'
                      AND p.account_id = %s
                      AND p.is_usable = TRUE
                      AND p.injection_flag = FALSE
                  )
                  OR
                  (c.source_type = 'COMMERCIAL' AND cr.account_id = %s)
              )
            ORDER BY c.citation_number
            """,
            (briefing_id, briefing["account_id"], briefing["account_id"]),
        )
        rows = cursor.fetchall()
    return BriefingCitationsResponse(
        briefing_id=briefing_id,
        citations=rows,
    )


def _render_briefing_pdf(briefing: BriefingResponse) -> bytes:
    lines = [
        "Customer 360 Briefing",
        "Internal customer report",
        f"Briefing: {briefing.briefing_id}",
        f"Account: {briefing.account_id}",
        f"Status: {briefing.status.value}",
    ]
    text_commands = ["BT", "/F1 12 Tf", "50 740 Td"]
    for index, line in enumerate(lines):
        escaped = line.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
        if index:
            text_commands.append("0 -22 Td")
        text_commands.append(f"({escaped}) Tj")
    text_commands.append("ET")
    stream = "\n".join(text_commands).encode("ascii")
    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
        b"/Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
        b"<< /Length "
        + str(len(stream)).encode("ascii")
        + b" >>\nstream\n"
        + stream
        + b"\nendstream",
    ]
    pdf = bytearray(b"%PDF-1.4\n")
    offsets = [0]
    for number, obj in enumerate(objects, start=1):
        offsets.append(len(pdf))
        pdf.extend(f"{number} 0 obj\n".encode("ascii") + obj + b"\nendobj\n")
    xref_offset = len(pdf)
    pdf.extend(f"xref\n0 {len(offsets)}\n".encode("ascii"))
    pdf.extend(b"0000000000 65535 f \n")
    for offset in offsets[1:]:
        pdf.extend(f"{offset:010} 00000 n \n".encode("ascii"))
    pdf.extend(
        f"trailer\n<< /Size {len(offsets)} /Root 1 0 R >>\n"
        f"startxref\n{xref_offset}\n%%EOF\n".encode("ascii")
    )
    return bytes(pdf)


@router.get(
    "/{briefing_id}/export",
    response_class=Response,
    summary="Download a briefing as an internal PDF",
    responses={
        200: {
            "description": "PDF file generated from a saved briefing.",
            "content": {"application/pdf": {"schema": {"type": "string", "format": "binary"}}},
        },
        403: {"model": ErrorResponse, "description": "ACC-002 Account access denied."},
        404: {"model": ErrorResponse, "description": "BRF-001 Briefing not found."},
        500: {"model": ErrorResponse, "description": "Database query failed."},
        503: {"model": ErrorResponse, "description": "Database is unavailable."},
    },
)
def export_briefing_pdf(
    briefing_id: UUID,
    user: dict = Depends(get_current_user),
    connection: Connection = Depends(get_db_connection),
) -> Response:
    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT id, account_id, site_id, briefing_status, is_stale, sections,
                   validation_status, created_at, completed_at
            FROM briefings
            WHERE id = %s
            """,
            (briefing_id,),
        )
        row = cursor.fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="Briefing not found.")
    check_account_access(user, row["account_id"])
    briefing = BriefingResponse(
        briefing_id=row["id"],
        account_id=row["account_id"],
        site_id=row["site_id"],
        status=row["briefing_status"],
        is_stale=row["is_stale"],
        sections=row["sections"],
        validation_status=row["validation_status"],
        created_at=row["created_at"],
        completed_at=row["completed_at"],
    )
    return Response(
        content=_render_briefing_pdf(briefing),
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="briefing-{briefing_id}.pdf"'
        },
    )
