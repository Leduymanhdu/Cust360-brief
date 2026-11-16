# ============================================================
# citations.py – FastAPI router cho Citations API
# KAN-20: FR-BRF-003 – GET /briefings/{briefing_id}/citations
# SDS Mục 3.3
# ============================================================

from __future__ import annotations

from typing import Literal
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

# ---------------------------------------------------------------------------
# Pydantic schemas
# ---------------------------------------------------------------------------

SourceType = Literal["PDF", "COMMERCIAL"]
ValidationStatus = Literal["PENDING", "VALID", "INVALID", "REJECTED"]


class CitationOut(BaseModel):
    """Schema trả về cho một trích dẫn.

    Căn cứ: SDS Mục 3.3 – FR-BRF-003
    """

    id: UUID
    briefing_id: UUID
    citation_number: int = Field(..., ge=1, description="Số thứ tự trích dẫn [n]")
    claim_text: str = Field(..., description="Câu khẳng định được trích dẫn")
    source_type: SourceType = Field(..., description="Loại nguồn: PDF hoặc COMMERCIAL")
    source_name: str = Field(..., description="Tên file PDF hoặc tên hệ thống thương mại")
    page_number: int | None = Field(
        None, description="Số trang (chỉ có khi source_type='PDF')"
    )
    source_excerpt: str | None = Field(
        None, description="Đoạn trích nguyên văn từ nguồn"
    )
    validation_status: ValidationStatus = Field(
        "PENDING", description="Trạng thái xác minh"
    )

    model_config = {"from_attributes": True}


class CitationsResponse(BaseModel):
    """Response body cho GET /briefings/{briefing_id}/citations."""

    briefing_id: UUID
    citations: list[CitationOut]


# ---------------------------------------------------------------------------
# Router
# ---------------------------------------------------------------------------

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
async def get_citations(
    briefing_id: UUID,
    # current_user = Depends(get_current_user),   # inject auth khi tích hợp
    # db: AsyncSession = Depends(get_db),         # inject DB session
) -> CitationsResponse:
    """
    Endpoint: GET /api/v1/briefings/{briefing_id}/citations

    Logic:
    1. Kiểm tra briefing tồn tại
    2. Kiểm tra current_user có quyền truy cập account của briefing
    3. Query bảng citations JOIN pdf_text (nếu PDF) hoặc commercial_records
    4. Map sang CitationOut schema
    5. Trả về sorted by citation_number

    Ví dụ SQL (pseudo):
        SELECT
            c.id, c.briefing_id, c.citation_number, c.claim_text,
            c.source_type, c.validation_status, c.source_excerpt,
            pt.file_name AS source_name,
            pt.page_number,
            cr.source_system AS source_name   -- khi COMMERCIAL
        FROM citations c
        LEFT JOIN pdf_text pt ON c.pdf_text_id = pt.id
        LEFT JOIN commercial_records cr ON c.commercial_record_id = cr.id
        WHERE c.briefing_id = :briefing_id
        ORDER BY c.citation_number ASC
    """
    # TODO: Thay bằng DB query thực tế
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="DB integration pending – schema & router ready",
    )
