from uuid import UUID
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import AccountSearchResponse, AccountSummary, ErrorResponse
from app.security import get_current_user
from app.services.user_service import search_accounts_by_scope

router = APIRouter(prefix="/accounts", tags=["Accounts"])


@router.get(
    "/search",
    response_model=AccountSearchResponse,
    summary="Search accounts by legal name or tax code within caller's account scope",
    responses={
        401: {"model": ErrorResponse, "description": "Authentication required."},
    },
)
def search_accounts(
    q: str = Query(
        min_length=1,
        max_length=200,
        description="Partial account name or exact/partial tax code.",
        examples=["ABC"],
    ),
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> AccountSearchResponse:
    """Return only accounts in the caller's authorized account scope from the database.

    Multiple matches require manual selection by the client.
    """
    query = q.strip()
    allowed_ids = user["account_ids"]

    db_accounts = search_accounts_by_scope(db, query, allowed_ids)
    
    # Map to AccountSummary
    results = []
    total_matches = len(db_accounts)

    for acc in db_accounts:
        match_status = (
            "EXACT"
            if acc.tax_code and acc.tax_code.casefold() == query.casefold()
            else "AMBIGUOUS"
            if total_matches > 1
            else "SINGLE"
        )
        results.append(
            AccountSummary(
                id=UUID(acc.id),
                legal_name=acc.legal_name,
                tax_code=acc.tax_code,
                industry=acc.industry,
                status=acc.status,
                match_status=match_status,
            )
        )

    return AccountSearchResponse(
        results=results,
        requires_manual_selection=len(results) > 1,
    )
