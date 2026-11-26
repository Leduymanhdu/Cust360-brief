"""Database queries and operations for Users and Accounts."""

from datetime import datetime, timezone
from uuid import UUID
from sqlalchemy.orm import Session
from app.models import User, Account, UserAccountAccess


def get_user_by_email(db: Session, email: str) -> User | None:
    """Find a user by case-insensitive email address."""
    return db.query(User).filter(User.email.ilike(email.strip())).first()


def get_user_by_id(db: Session, user_id: str | UUID) -> User | None:
    """Find a user by primary key ID."""
    return db.query(User).filter(User.id == str(user_id)).first()


def record_failed_login(db: Session, user: User, max_attempts: int, lock_until: datetime | None) -> None:
    """Increment failed login attempts and optionally set lock expiration."""
    user.failed_login_attempts = (user.failed_login_attempts or 0) + 1
    if lock_until:
        user.locked_until = lock_until
    db.commit()
    db.refresh(user)


def reset_failed_login(db: Session, user: User) -> None:
    """Reset failed login attempts counter and clear locked_until timestamp."""
    user.failed_login_attempts = 0
    user.locked_until = None
    db.commit()
    db.refresh(user)


def get_user_account_ids(db: Session, user_id: str | UUID, user_role: str) -> set[UUID]:
    """Retrieve allowed Account IDs within the user's account scope.
    
    If role is ADMIN, all active accounts are in scope.
    Otherwise, only accounts explicitly mapped in user_account_access are returned.
    """
    if user_role == "ADMIN":
        all_accounts = db.query(Account.id).all()
        return {UUID(acc_id[0]) for acc_id in all_accounts}

    records = db.query(UserAccountAccess.account_id).filter(
        UserAccountAccess.user_id == str(user_id)
    ).all()
    return {UUID(row[0]) for row in records}


def search_accounts_by_scope(
    db: Session,
    query: str,
    allowed_account_ids: set[UUID],
) -> list[Account]:
    """Search accounts by legal_name or tax_code, strictly constrained to allowed_account_ids."""
    if not allowed_account_ids:
        return []
    
    str_ids = [str(aid) for aid in allowed_account_ids]
    q = db.query(Account).filter(Account.id.in_(str_ids))
    
    clean_query = query.strip()
    if clean_query:
        search_pattern = f"%{clean_query}%"
        q = q.filter(
            (Account.legal_name.ilike(search_pattern)) |
            (Account.tax_code.ilike(search_pattern)) |
            (Account.industry.ilike(search_pattern))
        )
    return q.all()
