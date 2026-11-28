"""JWT token generation, decoding, and cryptographic validation."""

from datetime import datetime, timedelta, timezone
from typing import Any
import jwt
from pydantic import ValidationError

from app import config


def create_access_token(
    data: dict[str, Any],
    expires_delta: timedelta | None = None,
) -> str:
    """Encode payload claims into a cryptographically signed JWT.
    
    Claims include sub (user_id), email, role, and exp.
    """
    to_encode = data.copy()
    now = datetime.now(timezone.utc)
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=config.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({
        "exp": expire,
        "iat": now,
        "nbf": now,
    })
    
    encoded_jwt = jwt.encode(
        to_encode,
        config.JWT_SECRET_KEY,
        algorithm=config.JWT_ALGORITHM,
    )
    return encoded_jwt


def decode_access_token(token: str) -> dict[str, Any] | None:
    """Decode and cryptographically verify a JWT.
    
    Verifies signature and expiration time. Returns claims dict or None if invalid/expired.
    """
    try:
        payload = jwt.decode(
            token,
            config.JWT_SECRET_KEY,
            algorithms=[config.JWT_ALGORITHM],
            options={"require": ["exp", "sub"]},
        )
        return payload
    except (jwt.PyJWTError, ValidationError):
        return None
