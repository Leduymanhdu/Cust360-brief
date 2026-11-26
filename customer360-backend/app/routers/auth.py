"""Database-authenticated login router with password hash verification and JWT issuance."""

from datetime import datetime, timedelta, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import config
from app.database import get_db
from app.schemas import ErrorResponse, LoginRequest, LoginResponse, UserRole, UserSummary
from app.services.jwt_service import create_access_token
from app.services.password_service import verify_password
from app.services.user_service import (
    get_user_by_email,
    record_failed_login,
    reset_failed_login,
)

router = APIRouter(prefix="/auth", tags=["Authentication"])

# In-memory tracking for unknown emails (so lockout tests pass without leaking existence)
UNKNOWN_EMAIL_LOCKOUT: dict[str, dict[str, Any]] = {}


@router.post(
    "/login",
    response_model=LoginResponse,
    summary="Log in and receive a cryptographically signed JWT access token",
    responses={
        401: {"model": ErrorResponse, "description": "AUTH-001 Invalid credentials."},
        423: {"model": ErrorResponse, "description": "AUTH-002 Account locked."},
    },
)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> LoginResponse:
    """Authenticate user with database credentials and return signed JWT."""
    email = payload.email.lower().strip()
    now = datetime.now(timezone.utc)

    user = get_user_by_email(db, email)

    # 1. If user exists in DB, check DB lockout state
    if user:
        if user.locked_until:
            # Handle timezone comparison safely
            locked_until = user.locked_until
            if locked_until.tzinfo is None:
                locked_until = locked_until.replace(tzinfo=timezone.utc)
            if locked_until > now:
                raise HTTPException(
                    status_code=status.HTTP_423_LOCKED,
                    detail="Account locked after repeated failed login attempts.",
                )
            else:
                # Lockout period expired
                reset_failed_login(db, user)

        # Check if user account is disabled
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Account is inactive or disabled.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Verify password hash
        if not verify_password(payload.password, user.password_hash):
            attempts = (user.failed_login_attempts or 0) + 1
            lock_until = None
            if attempts >= config.MAX_FAILED_LOGIN_ATTEMPTS:
                lock_until = now + timedelta(minutes=config.ACCOUNT_LOCK_MINUTES)
            record_failed_login(db, user, config.MAX_FAILED_LOGIN_ATTEMPTS, lock_until)

            if lock_until:
                raise HTTPException(
                    status_code=status.HTTP_423_LOCKED,
                    detail="Account locked after repeated failed login attempts.",
                )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email or password is incorrect.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Successful login: reset failed counters
        reset_failed_login(db, user)

        # Create JWT token
        token_expires_seconds = config.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60
        access_token = create_access_token(
            data={
                "sub": user.id,
                "email": user.email,
                "role": user.role,
                "full_name": user.full_name,
            },
            expires_delta=timedelta(seconds=token_expires_seconds),
        )

        user_summary = UserSummary(
            id=UUID(user.id),
            email=user.email,
            role=UserRole(user.role),
            full_name=user.full_name,
        )

        return LoginResponse(
            access_token=access_token,
            expires_in=token_expires_seconds,
            user=user_summary,
        )

    # 2. Unknown user handling (protect against email enumeration and test lockout)
    state = UNKNOWN_EMAIL_LOCKOUT.setdefault(
        email,
        {"failed_attempts": 0, "locked_until": None},
    )
    locked_until = state["locked_until"]
    if isinstance(locked_until, datetime) and locked_until > now:
        raise HTTPException(
            status_code=status.HTTP_423_LOCKED,
            detail="Account locked after repeated failed login attempts.",
        )

    state["failed_attempts"] = int(state["failed_attempts"] or 0) + 1
    if state["failed_attempts"] >= config.MAX_FAILED_LOGIN_ATTEMPTS:
        state["locked_until"] = now + timedelta(minutes=config.ACCOUNT_LOCK_MINUTES)
        raise HTTPException(
            status_code=status.HTTP_423_LOCKED,
            detail="Account locked after repeated failed login attempts.",
        )

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Email or password is incorrect.",
        headers={"WWW-Authenticate": "Bearer"},
    )
