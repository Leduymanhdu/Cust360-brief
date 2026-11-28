from __future__ import annotations

from typing import Literal
from uuid import UUID

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

SourceType = Literal["PDF", "COMMERCIAL"]
ValidationStatus = Literal["PENDING", "VALID", "INVALID", "REJECTED"]


class CitationOut(BaseModel):
    id: UUID
    briefing_id: UUID
    citation_number: int = Field(..., ge=1)
    claim_text: str
    source_type: SourceType
    source_name: str
    page_number: int | None = None
    source_excerpt: str | None = None
    validation_status: ValidationStatus = "PENDING"

    model_config = {"from_attributes": True}


class CitationsResponse(BaseModel):
    briefing_id: UUID
    citations: list[CitationOut]


router = APIRouter(prefix="/briefings", tags=["citations"])


@router.get(
    "/{briefing_id}/citations",
    response_model=CitationsResponse,
    summary="Lấy danh sách citations của một briefing",
    description=(
        "Trả về tất cả trích dẫn của briefing, sắp xếp theo citation_number. "
        "Chỉ những người dùng có quyền truy cập account tương ứng mới được xem. "
        "**FR-BRF-003** (SDS Mục 3.3)"
    ),
    responses={
        200: {"description": "Danh sách citations"},
        401: {"description": "Chưa xác thực"},
        403: {"description": "Không có quyền truy cập briefing này"},
        404: {"description": "Briefing không tồn tại"},
    },
)
async def get_citations(briefing_id: UUID) -> CitationsResponse:
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="DB integration pending – schema & router ready",
    )
