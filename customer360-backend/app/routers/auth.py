from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, HTTPException, status

from app.mock_data import DEMO_USERS
from app.schemas import ErrorResponse, LoginRequest, LoginResponse

router = APIRouter(prefix="/auth", tags=["Authentication"])
LOGIN_STATE: dict[str, dict[str, datetime | int | None]] = {}


@router.post(
    "/login",
    response_model=LoginResponse,
    summary="Log in and receive a demo bearer token",
    responses={
        401: {"model": ErrorResponse, "description": "AUTH-001 Invalid credentials."},
        423: {"model": ErrorResponse, "description": "AUTH-002 Account locked."},
    },
)
def login(payload: LoginRequest) -> LoginResponse:
    """Authenticate one of the documented demo users.

    This integration build returns a fixed mock token. Replace this handler with
    the JWT/password-hash service before deploying to a shared environment.
    """
    email = payload.email.lower()
    state = LOGIN_STATE.setdefault(
        email,
        {"failed_attempts": 0, "locked_until": None},
    )
    now = datetime.now(timezone.utc)
    locked_until = state["locked_until"]
    if isinstance(locked_until, datetime) and locked_until > now:
        raise HTTPException(
            status_code=status.HTTP_423_LOCKED,
            detail="Account locked after repeated failed login attempts.",
        )
    if isinstance(locked_until, datetime):
        state["failed_attempts"] = 0
        state["locked_until"] = None

    account = DEMO_USERS.get(email)
    if account is None or payload.password != account["password"]:
        state["failed_attempts"] = int(state["failed_attempts"] or 0) + 1
        if state["failed_attempts"] >= 5:
            state["locked_until"] = now + timedelta(minutes=30)
            raise HTTPException(
                status_code=status.HTTP_423_LOCKED,
                detail="Account locked after repeated failed login attempts.",
            )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email or password is incorrect.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    state["failed_attempts"] = 0
    state["locked_until"] = None
    return LoginResponse(
        access_token=account["token"],
        expires_in=900,
        user=account["user"],
    )
