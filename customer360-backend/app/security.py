"""Database-backed Bearer authentication and role/account-scope authorization."""

from typing import Any
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User
from app.schemas import UserRole, UserSummary
from app.services.jwt_service import decode_access_token
from app.services.user_service import get_user_account_ids, get_user_by_id

bearer_scheme = HTTPBearer(
    auto_error=False,
    scheme_name="BearerAuth",
    description="Use the JWT access token returned by POST /api/v1/auth/login.",
)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    """Validate Bearer JWT token, verify user existence and active status in DB.
    
    Returns an authenticated context dict containing:
    - 'user': UserSummary
    - 'account_ids': set of accessible UUIDs (Account Scope)
    - 'db_user': User ORM instance
    """
    if credentials is None or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid bearer token.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token is invalid or expired.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token claims missing subject identifier.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Database query for live user
    user = get_user_by_id(db, user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authenticated user no longer exists.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is inactive or disabled.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Resolve account scope from database
    account_ids = get_user_account_ids(db, user.id, user.role)

    user_summary = UserSummary(
        id=UUID(user.id),
        email=user.email,
        role=UserRole(user.role),
        full_name=user.full_name,
    )

    return {
        "user": user_summary,
        "account_ids": account_ids,
        "db_user": user,
    }


def require_role(*allowed_roles: UserRole):
    """Factory dependency enforcing Role-Based Access Control (RBAC)."""
    def _role_checker(user: dict[str, Any] = Depends(get_current_user)) -> dict[str, Any]:
        user_role = user["user"].role
        if user_role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access forbidden: required role in {[r.value for r in allowed_roles]}, but user has role '{user_role.value}'.",
            )
        return user
    return _role_checker


def require_admin(user: dict[str, Any] = Depends(get_current_user)) -> dict[str, Any]:
    """Dependency enforcing ADMIN role."""
    if user["user"].role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Administrator role required.",
        )
    return user


def check_account_access(user: dict[str, Any], account_id: UUID) -> None:
    """Enforce Account Scope authorization.
    
    Admins bypass individual account restrictions.
    Non-admin users are restricted to assigned accounts in user_account_access.
    """
    if user["user"].role == UserRole.ADMIN:
        return
    if account_id not in user["account_ids"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bạn không có quyền truy cập tài khoản này.",
        )
