from fastapi import APIRouter, Depends, Query

from app.mock_data import ACCOUNTS
from app.schemas import AccountSearchResponse, ErrorResponse
from app.security import get_current_user

router = APIRouter(prefix="/accounts", tags=["Accounts"])


@router.get(
    "/search",
    response_model=AccountSearchResponse,
    summary="Search accounts by legal name or tax code",
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
) -> AccountSearchResponse:
    """Return only accounts in the caller's account scope.

    Multiple matches are never selected automatically; the client must show
    the candidates and let the user make a manual selection.
    """
    query = q.casefold().strip()
    allowed_ids = user["account_ids"]
    results = [
        account.model_copy(
            update={
                "match_status": (
                    "EXACT"
                    if account.tax_code and account.tax_code.casefold() == query
                    else "AMBIGUOUS"
                    if len(
                        [
                            candidate
                            for candidate in ACCOUNTS
                            if candidate.id in allowed_ids
                            and (
                                query in candidate.legal_name.casefold()
                                or (candidate.tax_code and query in candidate.tax_code.casefold())
                            )
                        ]
                    )
                    > 1
                    else "SINGLE"
                )
            }
        )
        for account in ACCOUNTS
        if account.id in allowed_ids
        and (
            query in account.legal_name.casefold()
            or (account.tax_code and query in account.tax_code.casefold())
        )
    ]
    return AccountSearchResponse(
        results=results,
        requires_manual_selection=len(results) > 1,
    )
