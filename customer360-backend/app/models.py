"""SQLAlchemy ORM models corresponding to database/init.sql."""

import uuid
from datetime import datetime, timezone
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
)
from sqlalchemy.orm import relationship

from app.database import Base


def _gen_uuid_str() -> str:
    return str(uuid.uuid4())


def _now() -> datetime:
    return datetime.now(timezone.utc)


class User(Base):
    """User entity representing system operators (ADMIN, SALES, SERVICE)."""
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=_gen_uuid_str)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(Text, nullable=False)
    full_name = Column(String(255), nullable=False)
    role = Column(String(30), nullable=False)  # 'ADMIN', 'SALES', 'SERVICE'
    is_active = Column(Boolean, default=True, nullable=False)
    failed_login_attempts = Column(Integer, default=0, nullable=False)
    locked_until = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=_now, onupdate=_now, nullable=False)

    account_accesses = relationship("UserAccountAccess", back_populates="user", cascade="all, delete-orphan")


class Account(Base):
    """Account entity representing customer enterprise organizations."""
    __tablename__ = "accounts"

    id = Column(String(36), primary_key=True, default=_gen_uuid_str)
    legal_name = Column(String(500), nullable=False, index=True)
    tax_code = Column(String(100), unique=True, nullable=True, index=True)
    industry = Column(String(255), nullable=True)
    status = Column(String(30), default="ACTIVE", nullable=False)  # 'ACTIVE', 'INACTIVE'
    created_at = Column(DateTime(timezone=True), default=_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=_now, onupdate=_now, nullable=False)

    sites = relationship("Site", back_populates="account", cascade="all, delete-orphan")
    user_accesses = relationship("UserAccountAccess", back_populates="account", cascade="all, delete-orphan")


class Site(Base):
    """Operational site or branch belonging to an enterprise account."""
    __tablename__ = "sites"

    id = Column(String(36), primary_key=True, default=_gen_uuid_str)
    account_id = Column(String(36), ForeignKey("accounts.id", ondelete="CASCADE"), nullable=False)
    site_name = Column(String(255), nullable=False)
    address = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=_now, nullable=False)

    account = relationship("Account", back_populates="sites")


class UserAccountAccess(Base):
    """Join table defining Account Scope permissions for users."""
    __tablename__ = "user_account_access"

    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    account_id = Column(String(36), ForeignKey("accounts.id", ondelete="CASCADE"), primary_key=True)
    granted_at = Column(DateTime(timezone=True), default=_now, nullable=False)

    user = relationship("User", back_populates="account_accesses")
    account = relationship("Account", back_populates="user_accesses")
