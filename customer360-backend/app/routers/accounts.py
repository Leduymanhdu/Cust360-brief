from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from psycopg import Connection

from app.database import get_db_connection
from app.schemas import (
    AccountDetail,
    AccountSearchResponse,
    AccountSite,
    AccountSummary,
    BriefingResponse,
    ErrorResponse,
)
from app.security import check_account_access, get_current_user

router = APIRouter(prefix="/accounts", tags=["Accounts"])


@router.get(
    "/search",
    response_model=AccountSearchResponse,
    summary="Search accounts by legal name or tax code",
    responses={
        401: {"model": ErrorResponse, "description": "Authentication required."},
        500: {"model": ErrorResponse, "description": "Database query failed."},
        503: {"model": ErrorResponse, "description": "Database is unavailable."},
    },
)
def search_accounts(
    q: str = Query(
        default="",
        max_length=200,
        description="Optional partial account name or exact/partial tax code. Empty returns all scoped accounts.",
        examples=["ABC"],
    ),
    user: dict = Depends(get_current_user),
    connection: Connection = Depends(get_db_connection),
) -> AccountSearchResponse:
    """Search PostgreSQL for accounts visible in the caller's account scope.

    Multiple matches are never selected automatically; the client must show
    the candidates and let the user make a manual selection.
    """
    query = q.strip()

    is_admin = user["user"].role.value == "ADMIN"
    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT a.id, a.legal_name, a.tax_code, a.industry, a.status
            FROM accounts AS a
            WHERE (
                %s = ''
                OR strpos(lower(a.legal_name), lower(%s)) > 0
                OR strpos(lower(COALESCE(a.tax_code, '')), lower(%s)) > 0
            )
            AND (
                %s
                OR EXISTS (
                    SELECT 1
                    FROM user_account_access AS access
                    WHERE access.user_id = %s
                      AND access.account_id = a.id
                )
            )
            ORDER BY a.legal_name, a.id
            """,
            (query, query, query, is_admin, user["user"].id),
        )
        rows = cursor.fetchall()

    ambiguous = len(rows) > 1
    results = [
        AccountSummary(
            id=row["id"],
            legal_name=row["legal_name"],
            tax_code=row["tax_code"],
            industry=row["industry"],
            status=row["status"],
            match_status=(
                "EXACT"
                if query and row["tax_code"] and row["tax_code"].casefold() == query.casefold()
                else "AMBIGUOUS"
                if ambiguous
                else "SINGLE"
            ),
        )
        for row in rows
    ]
    return AccountSearchResponse(
        results=results,
        requires_manual_selection=len(results) > 1,
    )


@router.get(
    "/{account_id}",
    response_model=AccountDetail,
    summary="Get account details and sites",
    responses={
        401: {"model": ErrorResponse, "description": "Authentication required."},
        403: {"model": ErrorResponse, "description": "Account access denied."},
        404: {"model": ErrorResponse, "description": "Account not found."},
        500: {"model": ErrorResponse, "description": "Database query failed."},
        503: {"model": ErrorResponse, "description": "Database is unavailable."},
    },
)
def get_account(
    account_id: UUID,
    user: dict = Depends(get_current_user),
    connection: Connection = Depends(get_db_connection),
) -> AccountDetail:
    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT a.id, a.legal_name, a.tax_code, a.industry, a.status,
                   s.id AS site_id, s.site_name, s.address
            FROM accounts AS a
            LEFT JOIN sites AS s ON s.account_id = a.id
            WHERE a.id = %s
            ORDER BY s.site_name, s.id
            """,
            (account_id,),
        )
        rows = cursor.fetchall()

    if not rows:
        raise HTTPException(status_code=404, detail="Account not found.")

    is_admin = user["user"].role.value == "ADMIN"
    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT EXISTS (
                SELECT 1
                FROM user_account_access
                WHERE user_id = %s AND account_id = %s
            ) AS has_access
            """,
            (user["user"].id, account_id),
        )
        has_access = cursor.fetchone()["has_access"]
    if not is_admin and not has_access:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bạn không có quyền truy cập tài khoản này.",
        )

    account = rows[0]
    return AccountDetail(
        id=account["id"],
        legal_name=account["legal_name"],
        tax_code=account["tax_code"],
        industry=account["industry"],
        status=account["status"],
        sites=[
            AccountSite(
                id=row["site_id"],
                site_name=row["site_name"],
                address=row["address"],
            )
            for row in rows
            if row["site_id"] is not None
        ],
    )


@router.get(
    "/{account_id}/briefings/latest",
    response_model=BriefingResponse,
    summary="Get the latest saved briefing for an account",
    responses={
        401: {"model": ErrorResponse, "description": "Authentication required."},
        403: {"model": ErrorResponse, "description": "Account access denied."},
        404: {"model": ErrorResponse, "description": "Account or briefing not found."},
        500: {"model": ErrorResponse, "description": "Database query failed."},
        503: {"model": ErrorResponse, "description": "Database is unavailable."},
    },
)
def get_latest_account_briefing(
    account_id: UUID,
    user: dict = Depends(get_current_user),
    connection: Connection = Depends(get_db_connection),
) -> BriefingResponse:
    with connection.cursor() as cursor:
        cursor.execute("SELECT 1 FROM accounts WHERE id = %s", (account_id,))
        if cursor.fetchone() is None:
            raise HTTPException(status_code=404, detail="Account not found.")

    check_account_access(user, account_id)
    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT id, account_id, site_id, briefing_status, is_stale, sections,
                   validation_status, created_at, completed_at
            FROM briefings
            WHERE account_id = %s
            ORDER BY created_at DESC, id DESC
            LIMIT 1
            """,
            (account_id,),
        )
        row = cursor.fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="No saved briefing for this account.")
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
