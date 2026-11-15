from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Response, status

from app.mock_data import (
    ACCOUNTS,
    BRIEFINGS,
    BRIEFING_CITATIONS,
    BRIEFING_ID,
    ACCOUNT_ABC_VIETNAM_ID,
    SITE_HANOI_ID,
    create_mock_briefing,
)
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
    },
)
def generate_briefing(
    payload: BriefingGenerationRequest,
    user: dict = Depends(get_current_user),
) -> BriefingAcceptedResponse:
    """Accept a generation request and create a deterministic mock briefing."""
    check_account_access(user, payload.account_id)
    if not any(account.id == payload.account_id for account in ACCOUNTS):
        raise HTTPException(status_code=404, detail="Account not found.")
    if payload.site_id is not None and (
        payload.account_id != ACCOUNT_ABC_VIETNAM_ID
        or payload.site_id != SITE_HANOI_ID
    ):
        raise HTTPException(status_code=404, detail="Site not found for this account.")

    briefing = create_mock_briefing(payload.account_id, payload.site_id)
    return BriefingAcceptedResponse(
        briefing_id=briefing.briefing_id,
        status="GENERATING",
        message="Briefing generation started (mock integration response).",
    )


@router.get(
    "/{briefing_id}",
    response_model=BriefingResponse,
    summary="Get a briefing and all six sections",
    responses={
        403: {"model": ErrorResponse, "description": "ACC-002 Account access denied."},
        404: {"model": ErrorResponse, "description": "BRF-001 Briefing not found."},
    },
)
def get_briefing(
    briefing_id: UUID,
    user: dict = Depends(get_current_user),
) -> BriefingResponse:
    briefing = BRIEFINGS.get(briefing_id)
    if briefing is None:
        raise HTTPException(status_code=404, detail="Briefing not found.")
    check_account_access(user, briefing.account_id)
    return briefing


@router.get(
    "/{briefing_id}/citations",
    response_model=BriefingCitationsResponse,
    summary="List the validated source citations for a briefing",
    responses={
        403: {"model": ErrorResponse, "description": "ACC-002 Account access denied."},
        404: {"model": ErrorResponse, "description": "BRF-001 Briefing not found."},
    },
)
def get_briefing_citations(
    briefing_id: UUID,
    user: dict = Depends(get_current_user),
) -> BriefingCitationsResponse:
    briefing = BRIEFINGS.get(briefing_id)
    if briefing is None:
        raise HTTPException(status_code=404, detail="Briefing not found.")
    check_account_access(user, briefing.account_id)
    return BriefingCitationsResponse(
        briefing_id=briefing_id,
        citations=BRIEFING_CITATIONS.get(briefing_id, []),
    )


def _mock_pdf(briefing: BriefingResponse) -> bytes:
    lines = [
        "Customer 360 Briefing",
        "MOCK INTEGRATION DOCUMENT - NOT AN OFFICIAL CUSTOMER REPORT",
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
            "description": "PDF file (watermarked as mock integration output).",
            "content": {"application/pdf": {"schema": {"type": "string", "format": "binary"}}},
        },
        403: {"model": ErrorResponse, "description": "ACC-002 Account access denied."},
        404: {"model": ErrorResponse, "description": "BRF-001 Briefing not found."},
    },
)
def export_briefing_pdf(
    briefing_id: UUID,
    user: dict = Depends(get_current_user),
) -> Response:
    briefing = BRIEFINGS.get(briefing_id)
    if briefing is None:
        raise HTTPException(status_code=404, detail="Briefing not found.")
    check_account_access(user, briefing.account_id)
    return Response(
        content=_mock_pdf(briefing),
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="briefing-{briefing_id}.pdf"'
        },
    )
