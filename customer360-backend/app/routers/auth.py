import logging
from datetime import datetime, timedelta, timezone

import bcrypt
from fastapi import APIRouter, Depends, HTTPException, status
from psycopg import Connection

from app.database import get_db_connection
from app.schemas import ErrorResponse, LoginRequest, LoginResponse
from app.security import create_access_token

router = APIRouter(prefix="/auth", tags=["Authentication"])
logger = logging.getLogger(__name__)


@router.post(
    "/login",
    response_model=LoginResponse,
    summary="Log in and receive a bearer token",
    responses={
        401: {"model": ErrorResponse, "description": "AUTH-001 Invalid credentials."},
        423: {"model": ErrorResponse, "description": "AUTH-002 Account locked."},
        500: {"model": ErrorResponse, "description": "Stored credential data is invalid."},
        503: {"model": ErrorResponse, "description": "Database is unavailable."},
    },
)
def login(
    payload: LoginRequest,
    connection: Connection = Depends(get_db_connection),
) -> LoginResponse:
    """Authenticate a database user and issue a short-lived JWT."""
    email = str(payload.email).casefold()
    now = datetime.now(timezone.utc)
    invalid_credentials = False
    lock_account = False
    invalid_hash = False

    with connection.transaction():
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT id, email, password_hash, full_name, role, is_active,
                       failed_login_attempts, locked_until
                FROM users
                WHERE lower(email) = %s
                FOR UPDATE
                """,
                (email,),
            )
            account = cursor.fetchone()
            if account is None or not account["is_active"]:
                invalid_credentials = True
            elif account["locked_until"] and account["locked_until"] > now:
                raise HTTPException(
                    status_code=status.HTTP_423_LOCKED,
                    detail="Account locked after repeated failed login attempts.",
                )
            else:
                failed_attempts = int(account["failed_login_attempts"] or 0)
                if account["locked_until"]:
                    cursor.execute(
                        """
                        UPDATE users
                        SET failed_login_attempts = 0, locked_until = NULL
                        WHERE id = %s
                        """,
                        (account["id"],),
                    )
                    failed_attempts = 0

                try:
                    password_matches = bcrypt.checkpw(
                        payload.password.encode("utf-8"),
                        account["password_hash"].encode("utf-8"),
                    )
                except ValueError:
                    logger.exception("Invalid password hash for user %s", account["id"])
                    invalid_hash = True
                    password_matches = False

                if not invalid_hash:
                    if not password_matches:
                        failed_attempts += 1
                        lock_account = failed_attempts >= 5
                        locked_until = now + timedelta(minutes=30) if lock_account else None
                        cursor.execute(
                            """
                            UPDATE users
                            SET failed_login_attempts = %s, locked_until = %s
                            WHERE id = %s
                            """,
                            (failed_attempts, locked_until, account["id"]),
                        )
                        invalid_credentials = not lock_account
                    else:
                        cursor.execute(
                            """
                            UPDATE users
                            SET failed_login_attempts = 0, locked_until = NULL
                            WHERE id = %s
                            """,
                            (account["id"],),
                        )

    if invalid_hash:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Stored password hash is invalid.",
        )
    if lock_account:
        raise HTTPException(
            status_code=status.HTTP_423_LOCKED,
            detail="Account locked after repeated failed login attempts.",
        )
    if invalid_credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email hoặc mật khẩu không chính xác.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return LoginResponse(
        access_token=create_access_token(account["id"]),
        expires_in=900,
        user={
            "id": account["id"],
            "email": account["email"],
            "role": account["role"],
            "full_name": account["full_name"],
        },
    )
