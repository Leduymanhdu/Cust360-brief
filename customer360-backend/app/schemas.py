"""Public request and response models used by the Customer 360 API."""

from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class APIModel(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={"examples": []},
    )


class ErrorResponse(APIModel):
    detail: str = Field(description="Human-readable error message.")
    code: str | None = Field(default=None, description="Stable application error code.")


class UserRole(str, Enum):
    ADMIN = "ADMIN"
    SALES = "SALES"
    SERVICE = "SERVICE"


class UserSummary(APIModel):
    id: UUID
    email: EmailStr
    role: UserRole
    full_name: str


class LoginRequest(APIModel):
    email: EmailStr = Field(examples=["sales@songnhat.com.vn"])
    password: str = Field(min_length=1, examples=["SecurePass123!"])


class LoginResponse(APIModel):
    access_token: str = Field(description="Bearer access token; mock token in this integration build.")
    token_type: Literal["Bearer"] = "Bearer"
    expires_in: int = Field(default=900, description="Access-token lifetime in seconds.")
    user: UserSummary


class AccountSummary(APIModel):
    id: UUID
    legal_name: str
    tax_code: str | None = None
    industry: str | None = None
    status: Literal["ACTIVE", "INACTIVE"] = "ACTIVE"
    match_status: Literal["EXACT", "AMBIGUOUS", "SINGLE"] = "SINGLE"


class AccountSearchResponse(APIModel):
    results: list[AccountSummary]
    requires_manual_selection: bool = Field(
        description="True when the user must choose among multiple matches."
    )


class BriefingGenerationRequest(APIModel):
    account_id: UUID
    site_id: UUID | None = Field(
        default=None,
        description="Optional site. Omit or send null to create a company-level briefing.",
    )


class BriefingAcceptedResponse(APIModel):
    briefing_id: UUID
    status: Literal["GENERATING"] = "GENERATING"
    message: str = "Briefing generation started"


class BriefingStatus(str, Enum):
    GENERATING = "GENERATING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    BLOCKED = "BLOCKED"


class BriefingSection(APIModel):
    content: str
    citations: list[int] = Field(default_factory=list)


class BriefingSections(APIModel):
    account_and_site: BriefingSection
    contacts_and_roles: BriefingSection
    recent_interactions: BriefingSection
    commercial_facts: BriefingSection
    service_issues: BriefingSection
    suggested_questions_and_gaps: BriefingSection


class BriefingResponse(APIModel):
    briefing_id: UUID
    account_id: UUID
    site_id: UUID | None = None
    status: BriefingStatus
    is_stale: bool = False
    sections: BriefingSections
    validation_status: Literal["PENDING", "PASSED", "FAILED", "BLOCKED"]
    created_at: datetime
    completed_at: datetime | None = None


class CitationItem(APIModel):
    citation_number: int = Field(ge=1)
    claim_text: str
    source_type: Literal["PDF", "COMMERCIAL"]
    source_id: UUID
    page_number: int | None = None
    source_excerpt: str | None = None
    validation_status: Literal["PENDING", "VALID", "INVALID", "REJECTED"]


class BriefingCitationsResponse(APIModel):
    briefing_id: UUID
    citations: list[CitationItem]


class ImportJobResponse(APIModel):
    job_id: UUID
    status: Literal["PROCESSING"] = "PROCESSING"
    records_received: int = Field(ge=0)
    message: str = "Import accepted for processing."


class RevokeAccessRequest(APIModel):
    account_id: UUID
    reason: str = Field(min_length=1, max_length=500)


class RevokeAccessResponse(APIModel):
    user_id: UUID
    account_id: UUID
    revoked: bool
    cache_cleared: bool
    message: str


class CommercialFacts(APIModel):
    account_id: UUID
    currency: Literal["VND", "USD"]
    quotation_total: Decimal
    order_total: Decimal
    record_count: int = Field(ge=0)
    as_of: date
