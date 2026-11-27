"""JWT authentication and database-backed account-scope checks."""

import os
from datetime import datetime, timedelta, timezone
from typing import Any
from uuid import UUID

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from psycopg import Connection

from app.database import get_db_connection
from app.schemas import UserRole, UserSummary

bearer_scheme = HTTPBearer(
    auto_error=False,
    scheme_name="BearerAuth",
    description="Use the access token returned by POST /api/v1/auth/login.",
)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    connection: Connection = Depends(get_db_connection),
) -> dict[str, Any]:
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid bearer token.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    secret = os.getenv("JWT_SECRET_KEY")
    if not secret:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="JWT signing is not configured.",
        )
    try:
        claims = jwt.decode(
            credentials.credentials,
            secret,
            algorithms=["HS256"],
            options={"require": ["sub", "exp"]},
        )
        user_id = UUID(claims["sub"])
    except (jwt.InvalidTokenError, KeyError, TypeError, ValueError) as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid bearer token.",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc

    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT id, email, role, full_name, is_active
            FROM users
            WHERE id = %s
            """,
            (user_id,),
        )
        row = cursor.fetchone()
        if row is None or not row["is_active"]:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User is inactive or no longer exists.",
                headers={"WWW-Authenticate": "Bearer"},
            )
        cursor.execute(
            "SELECT account_id FROM user_account_access WHERE user_id = %s",
            (user_id,),
        )
        account_ids = {access["account_id"] for access in cursor.fetchall()}

    return {
        "user": UserSummary(
            id=row["id"],
            email=row["email"],
            role=row["role"],
            full_name=row["full_name"],
        ),
        "account_ids": account_ids,
    }


def create_access_token(user_id: UUID) -> str:
    secret = os.getenv("JWT_SECRET_KEY")
    if not secret:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="JWT signing is not configured.",
        )
    now = datetime.now(timezone.utc)
    return jwt.encode(
        {
            "sub": str(user_id),
            "iat": now,
            "exp": now + timedelta(minutes=15),
        },
        secret,
        algorithm="HS256",
    )


def check_account_access(user: dict[str, Any], account_id: UUID) -> None:
    if user["user"].role == UserRole.ADMIN:
        return
    if account_id not in user["account_ids"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bạn không có quyền truy cập tài khoản này.",
        )


def require_admin(user: dict[str, Any] = Depends(get_current_user)) -> dict[str, Any]:
    if user["user"].role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Administrator role required.",
        )
    return user
