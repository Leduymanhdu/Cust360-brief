"""Comprehensive unit and integration tests for Authentication, Password Hashing, JWT, Middleware, RBAC, and Account Scope."""

import asyncio
from typing import Any
from uuid import UUID, uuid4
import httpx
import pytest

from app.database import SessionLocal
from app.main import app
from app.models import User
from app.services.jwt_service import create_access_token
from app.services.password_service import hash_password, verify_password
from app.services.db_seeder import (
    SALES_USER_ID,
    ADMIN_USER_ID,
    SERVICE_USER_ID,
    INACTIVE_USER_ID,
    ACCOUNT_ABC_VIETNAM_ID,
    ACCOUNT_ABC_COMPANY_ID,
    ACCOUNT_RESTRICTED_ID,
)


def request(method: str, path: str, **kwargs: Any) -> httpx.Response:
    async def send() -> httpx.Response:
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app),
            base_url="http://test",
        ) as client:
            return await client.request(method, path, **kwargs)

    return asyncio.run(send())


def test_password_hashing_and_verification():
    """Verify password hashing creates secure hashes and verifies properly."""
    raw_pwd = "MySecretPassword!2026"
    hashed = hash_password(raw_pwd)

    assert hashed != raw_pwd
    assert not hashed.startswith("MySecretPassword")
    assert verify_password(raw_pwd, hashed) is True
    assert verify_password("WrongPassword", hashed) is False
    assert verify_password("", hashed) is False


def test_login_success_with_database():
    """Login with valid DB credentials returns 200, JWT token and user info without password."""
    resp = request(
        "POST",
        "/api/v1/auth/login",
        json={"email": "sales@songnhat.com.vn", "password": "SecurePass123!"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert data["token_type"] == "Bearer"
    assert data["user"]["email"] == "sales@songnhat.com.vn"
    assert data["user"]["role"] == "SALES"
    assert "password" not in data
    assert "password_hash" not in data


def test_login_invalid_password():
    """Login with wrong password returns 401 Unauthorized."""
    resp = request(
        "POST",
        "/api/v1/auth/login",
        json={"email": "sales@songnhat.com.vn", "password": "WrongPassword!"},
    )
    assert resp.status_code == 401
    assert "detail" in resp.json()


def test_login_nonexistent_account():
    """Login with non-existent email returns 401 without revealing user existence."""
    resp = request(
        "POST",
        "/api/v1/auth/login",
        json={"email": "nonexistent_user_999@songnhat.com.vn", "password": "SomePassword123!"},
    )
    assert resp.status_code == 401
    assert resp.json()["detail"] == "Email or password is incorrect."


def test_login_inactive_disabled_account():
    """Login with inactive account is rejected with 401."""
    resp = request(
        "POST",
        "/api/v1/auth/login",
        json={"email": "inactive@songnhat.com.vn", "password": "InactivePass123!"},
    )
    assert resp.status_code == 401
    assert "inactive" in resp.json()["detail"].lower()


def test_protected_endpoint_without_token():
    """Accessing protected endpoint without Bearer header returns 401."""
    resp = request("GET", "/api/v1/accounts/search?q=ABC")
    assert resp.status_code == 401


def test_protected_endpoint_with_invalid_token():
    """Accessing protected endpoint with malformed/forged token returns 401."""
    resp = request(
        "GET",
        "/api/v1/accounts/search?q=ABC",
        headers={"Authorization": "Bearer totally-invalid-token-string"},
    )
    assert resp.status_code == 401


def test_protected_endpoint_with_expired_token():
    """Accessing protected endpoint with expired token returns 401."""
    import datetime
    from app.services.jwt_service import create_access_token
    
    # Create expired token (-10 minutes)
    expired_token = create_access_token(
        data={"sub": str(SALES_USER_ID), "email": "sales@songnhat.com.vn", "role": "SALES"},
        expires_delta=datetime.timedelta(minutes=-10),
    )
    resp = request(
        "GET",
        "/api/v1/accounts/search?q=ABC",
        headers={"Authorization": f"Bearer {expired_token}"},
    )
    assert resp.status_code == 401


def test_role_based_access_control_admin_only_endpoint():
    """SALES role user accessing ADMIN-only endpoint receives 403 Forbidden."""
    # 1. Login as sales
    sales_login = request(
        "POST",
        "/api/v1/auth/login",
        json={"email": "sales@songnhat.com.vn", "password": "SecurePass123!"},
    )
    sales_token = sales_login.json()["access_token"]
    sales_headers = {"Authorization": f"Bearer {sales_token}"}

    # Access admin import
    resp = request(
        "POST",
        "/api/v1/admin/import/csv",
        headers=sales_headers,
        files={"file": ("accounts.csv", b"name,tax_code\nTest,123", "text/csv")},
    )
    assert resp.status_code == 403
    assert "Administrator role required" in resp.json()["detail"]


def test_admin_accesses_admin_endpoint_successfully():
    """ADMIN role user accessing ADMIN endpoint receives 200."""
    admin_login = request(
        "POST",
        "/api/v1/auth/login",
        json={"email": "admin@songnhat.com.vn", "password": "AdminPass123!"},
    )
    admin_token = admin_login.json()["access_token"]
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    resp = request(
        "POST",
        "/api/v1/admin/import/csv",
        headers=admin_headers,
        files={"file": ("accounts.csv", b"name,tax_code\nTest,123", "text/csv")},
    )
    assert resp.status_code == 200
    assert resp.json()["records_received"] == 1


def test_account_scope_sales_user_within_scope():
    """Sales user searching accounts only sees accounts in their assigned scope."""
    sales_login = request(
        "POST",
        "/api/v1/auth/login",
        json={"email": "sales@songnhat.com.vn", "password": "SecurePass123!"},
    )
    sales_token = sales_login.json()["access_token"]
    sales_headers = {"Authorization": f"Bearer {sales_token}"}

    # Search for ABC accounts (in sales scope)
    resp = request("GET", "/api/v1/accounts/search?q=ABC", headers=sales_headers)
    assert resp.status_code == 200
    results = resp.json()["results"]
    result_ids = {r["id"] for r in results}
    assert str(ACCOUNT_ABC_VIETNAM_ID) in result_ids
    assert str(ACCOUNT_ABC_COMPANY_ID) in result_ids
    assert str(ACCOUNT_RESTRICTED_ID) not in result_ids


def test_account_scope_sales_user_denied_out_of_scope_account():
    """Sales user generating briefing for restricted account (out of scope) is blocked with 403."""
    sales_login = request(
        "POST",
        "/api/v1/auth/login",
        json={"email": "sales@songnhat.com.vn", "password": "SecurePass123!"},
    )
    sales_token = sales_login.json()["access_token"]
    sales_headers = {"Authorization": f"Bearer {sales_token}"}

    # Restricted account is not granted to Sales
    resp = request(
        "POST",
        "/api/v1/briefings/generate",
        headers=sales_headers,
        json={"account_id": str(ACCOUNT_RESTRICTED_ID)},
    )
    assert resp.status_code == 403
    assert "không có quyền" in resp.json()["detail"].lower()


def test_account_scope_admin_accesses_all_accounts():
    """Admin has global account scope and can access restricted accounts."""
    admin_login = request(
        "POST",
        "/api/v1/auth/login",
        json={"email": "admin@songnhat.com.vn", "password": "AdminPass123!"},
    )
    admin_token = admin_login.json()["access_token"]
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    # Search returns all accounts for admin
    resp = request("GET", "/api/v1/accounts/search?q=Hai Ha", headers=admin_headers)
    assert resp.status_code == 200
    results = resp.json()["results"]
    assert any(r["id"] == str(ACCOUNT_RESTRICTED_ID) for r in results)
