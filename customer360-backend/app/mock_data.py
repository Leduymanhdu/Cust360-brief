"""Deterministic fixtures for frontend integration before database wiring."""

from datetime import date, datetime, timezone
from decimal import Decimal
from uuid import UUID, uuid4

from app.schemas import (
    AccountSummary,
    BriefingResponse,
    BriefingSection,
    BriefingSections,
    BriefingStatus,
    CitationItem,
    UserRole,
    UserSummary,
)

SALES_USER_ID = UUID("10000000-0000-4000-8000-000000000001")
ADMIN_USER_ID = UUID("10000000-0000-4000-8000-000000000002")
ACCOUNT_ABC_VIETNAM_ID = UUID("20000000-0000-4000-8000-000000000001")
ACCOUNT_ABC_COMPANY_ID = UUID("20000000-0000-4000-8000-000000000002")
ACCOUNT_RESTRICTED_ID = UUID("20000000-0000-4000-8000-000000000003")
SITE_HANOI_ID = UUID("30000000-0000-4000-8000-000000000001")
BRIEFING_ID = UUID("40000000-0000-4000-8000-000000000001")
PDF_SOURCE_ID = UUID("50000000-0000-4000-8000-000000000001")
COMMERCIAL_SOURCE_ID = UUID("60000000-0000-4000-8000-000000000001")

DEMO_USERS = {
    "sales@songnhat.com.vn": {
        "password": "SecurePass123!",
        "token": "demo-sales-token",
        "user": UserSummary(
            id=SALES_USER_ID,
            email="sales@songnhat.com.vn",
            role=UserRole.SALES,
            full_name="Nguyen Van A",
        ),
        "account_ids": {ACCOUNT_ABC_VIETNAM_ID, ACCOUNT_ABC_COMPANY_ID},
    },
    "admin@songnhat.com.vn": {
        "password": "AdminPass123!",
        "token": "demo-admin-token",
        "user": UserSummary(
            id=ADMIN_USER_ID,
            email="admin@songnhat.com.vn",
            role=UserRole.ADMIN,
            full_name="SongNhat Admin",
        ),
        "account_ids": {
            ACCOUNT_ABC_VIETNAM_ID,
            ACCOUNT_ABC_COMPANY_ID,
            ACCOUNT_RESTRICTED_ID,
        },
    },
}

TOKEN_USERS = {
    account["token"]: account for account in DEMO_USERS.values()
}

ACCOUNTS = [
    AccountSummary(
        id=ACCOUNT_ABC_VIETNAM_ID,
        legal_name="ABC Vietnam Ltd",
        tax_code="0123456789",
        industry="Manufacturing",
        match_status="AMBIGUOUS",
    ),
    AccountSummary(
        id=ACCOUNT_ABC_COMPANY_ID,
        legal_name="ABC Vietnam Company",
        tax_code="0987654321",
        industry="Industrial equipment",
        match_status="AMBIGUOUS",
    ),
    AccountSummary(
        id=ACCOUNT_RESTRICTED_ID,
        legal_name="Hai Ha Industrial JSC",
        tax_code="0102030405",
        industry="Food manufacturing",
    ),
]

NOW = datetime.now(timezone.utc)

_citation_items = [
    CitationItem(
        citation_number=1,
        claim_text="ABC Vietnam Ltd is an active manufacturing account.",
        source_type="PDF",
        source_id=PDF_SOURCE_ID,
        page_number=3,
        source_excerpt="ABC Vietnam Ltd - manufacturing facility overview.",
        validation_status="VALID",
    ),
    CitationItem(
        citation_number=2,
        claim_text="The account has 1,000,000,000 VND in active orders.",
        source_type="COMMERCIAL",
        source_id=COMMERCIAL_SOURCE_ID,
        source_excerpt="ORDER / CONFIRMED / VND / 1,000,000,000",
        validation_status="VALID",
    ),
]

_sections = BriefingSections(
    account_and_site=BriefingSection(
        content="ABC Vietnam Ltd operates a manufacturing facility in Hanoi.",
        citations=[1],
    ),
    contacts_and_roles=BriefingSection(
        content="Contact and role information is not available in this mock dataset.",
        citations=[],
    ),
    recent_interactions=BriefingSection(
        content="No recent interaction records are available in this mock dataset.",
        citations=[],
    ),
    commercial_facts=BriefingSection(
        content="Active order total: 1,000,000,000 VND.",
        citations=[2],
    ),
    service_issues=BriefingSection(
        content="No service issues are recorded in this mock dataset.",
        citations=[],
    ),
    suggested_questions_and_gaps=BriefingSection(
        content="Confirm current production demand and identify the operational decision maker.",
        citations=[],
    ),
)

BRIEFINGS: dict[UUID, BriefingResponse] = {
    BRIEFING_ID: BriefingResponse(
        briefing_id=BRIEFING_ID,
        account_id=ACCOUNT_ABC_VIETNAM_ID,
        site_id=SITE_HANOI_ID,
        status=BriefingStatus.COMPLETED,
        is_stale=False,
        sections=_sections,
        validation_status="PASSED",
        created_at=NOW,
        completed_at=NOW,
    )
}

BRIEFING_CITATIONS: dict[UUID, list[CitationItem]] = {
    BRIEFING_ID: _citation_items
}


def create_mock_briefing(account_id: UUID, site_id: UUID | None) -> BriefingResponse:
    briefing_id = uuid4()
    briefing = BriefingResponse(
        briefing_id=briefing_id,
        account_id=account_id,
        site_id=site_id,
        status=BriefingStatus.COMPLETED,
        is_stale=False,
        sections=_sections,
        validation_status="PASSED",
        created_at=datetime.now(timezone.utc),
        completed_at=datetime.now(timezone.utc),
    )
    BRIEFINGS[briefing_id] = briefing
    BRIEFING_CITATIONS[briefing_id] = _citation_items
    return briefing


MOCK_COMMERCIAL_FACTS = {
    "currency": "VND",
    "quotation_total": Decimal("2500000000.00"),
    "order_total": Decimal("1000000000.00"),
    "record_count": 3,
    "as_of": date.today(),
}
