"""Secure password hashing and verification using BCrypt and Argon2id."""

import bcrypt
from app import config

try:
    from argon2 import PasswordHasher
    from argon2.exceptions import VerifyMismatchError
    _argon2_hasher = PasswordHasher()
except ImportError:
    _argon2_hasher = None


def hash_password(plain_password: str) -> str:
    """Hash a plaintext password securely.
    
    Supports bcrypt and argon2. Defaults to bcrypt.
    """
    if config.PASSWORD_HASH_ALGORITHM.lower() == "argon2" and _argon2_hasher:
        return _argon2_hasher.hash(plain_password)
    
    # BCrypt hashing
    salt = bcrypt.gensalt(rounds=12)
    hashed_bytes = bcrypt.hashpw(plain_password.encode("utf-8"), salt)
    return hashed_bytes.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plaintext password against a stored hash securely.
    
    Automatically detects hash algorithm (Argon2 vs BCrypt) and prevents timing attacks.
    """
    if not hashed_password or not plain_password:
        return False

    # Argon2 hash format: $argon2id$... or $argon2i$...
    if hashed_password.startswith("$argon2"):
        if not _argon2_hasher:
            return False
        try:
            return _argon2_hasher.verify(hashed_password, plain_password)
        except (VerifyMismatchError, Exception):
            return False

    # BCrypt hash format: $2a$, $2b$, $2y$...
    try:
        return bcrypt.checkpw(
            plain_password.encode("utf-8"),
            hashed_password.encode("utf-8"),
        )
    except (ValueError, TypeError, Exception):
        return False
