import asyncio
from typing import Any
import jwt
import httpx
import pytest

from app.main import app
from app.mock_data import (
    ACCOUNT_ABC_VIETNAM_ID,
    ACCOUNT_RESTRICTED_ID,
    BRIEFING_ID,
    SALES_USER_ID,
    ADMIN_USER_ID,
    SITE_HANOI_ID,
)
from app.services.jwt_service import create_access_token


def get_token_headers(user_id: str, email: str, role: str, full_name: str) -> dict[str, str]:
    token = create_access_token(
        data={
            "sub": user_id,
            "email": email,
            "role": role,
            "full_name": full_name,
        }
    )
    return {"Authorization": f"Bearer {token}"}


SALES_HEADERS = get_token_headers(
    str(SALES_USER_ID),
    "sales@songnhat.com.vn",
    "SALES",
    "Nguyen Van A",
)
ADMIN_HEADERS = get_token_headers(
    str(ADMIN_USER_ID),
    "admin@songnhat.com.vn",
    "ADMIN",
    "SongNhat Admin",
)


def request(method: str, path: str, **kwargs: Any) -> httpx.Response:
    async def send() -> httpx.Response:
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app),
            base_url="http://test",
        ) as client:
            return await client.request(method, path, **kwargs)

    return asyncio.run(send())


def test_openapi_documents_api_contract_and_bearer_security() -> None:
    docs = request("GET", "/docs")
    assert docs.status_code == 200
    assert "swagger-ui" in docs.text.lower()

    response = request("GET", "/openapi.json")
    assert response.status_code == 200
    document = response.json()
    assert "/api/v1/auth/login" in document["paths"]
    assert "/api/v1/admin/import/csv" in document["paths"]
    assert "/api/v1/admin/import/pdf" in document["paths"]
    assert "/api/v1/admin/users/{user_id}/revoke-access" in document["paths"]
    assert "/api/v1/briefings/{briefing_id}/export" in document["paths"]
    assert "BearerAuth" in document["components"]["securitySchemes"]
    assert document["paths"]["/api/v1/accounts/search"]["get"]["security"] == [
        {"BearerAuth": []}
    ]
    briefing_schema = document["components"]["schemas"]["BriefingSections"]
    assert set(briefing_schema["required"]) == {
        "account_and_site",
        "contacts_and_roles",
        "recent_interactions",
        "commercial_facts",
        "service_issues",
        "suggested_questions_and_gaps",
    }


def test_login_and_ambiguous_account_search() -> None:
    login = request(
        "POST",
        "/api/v1/auth/login",
        json={
            "email": "sales@songnhat.com.vn",
            "password": "SecurePass123!",
        },
    )
    assert login.status_code == 200
    token = login.json()["access_token"]
    assert token is not None
    assert len(token) > 20

    # Search using the returned real JWT token
    headers = {"Authorization": f"Bearer {token}"}
    search = request(
        "GET",
        "/api/v1/accounts/search",
        params={"q": "ABC"},
        headers=headers,
    )
    assert search.status_code == 200
    body = search.json()
    assert len(body["results"]) == 2
    assert body["requires_manual_selection"] is True


def test_briefing_citations_and_pdf_export() -> None:
    briefing = request(
        "GET",
        f"/api/v1/briefings/{BRIEFING_ID}",
        headers=SALES_HEADERS,
    )
    assert briefing.status_code == 200
    assert briefing.json()["status"] == "COMPLETED"
    assert len(briefing.json()["sections"]) == 6

    citations = request(
        "GET",
        f"/api/v1/briefings/{BRIEFING_ID}/citations",
        headers=SALES_HEADERS,
    )
    assert citations.status_code == 200
    assert [item["citation_number"] for item in citations.json()["citations"]] == [1, 2]

    export = request(
        "GET",
        f"/api/v1/briefings/{BRIEFING_ID}/export",
        headers=SALES_HEADERS,
    )
    assert export.status_code == 200
    assert export.headers["content-type"] == "application/pdf"
    assert export.content.startswith(b"%PDF-1.4")


def test_generate_briefing_returns_accepted_and_can_be_retrieved() -> None:
    accepted = request(
        "POST",
        "/api/v1/briefings/generate",
        headers=SALES_HEADERS,
        json={
            "account_id": str(ACCOUNT_ABC_VIETNAM_ID),
            "site_id": str(SITE_HANOI_ID),
        },
    )
    assert accepted.status_code == 202
    assert accepted.json()["status"] == "GENERATING"

    briefing = request(
        "GET",
        f"/api/v1/briefings/{accepted.json()['briefing_id']}",
        headers=SALES_HEADERS,
    )
    assert briefing.status_code == 200
    assert briefing.json()["status"] == "COMPLETED"


def test_account_scope_blocks_cross_account_access() -> None:
    response = request(
        "POST",
        "/api/v1/briefings/generate",
        headers=SALES_HEADERS,
        json={"account_id": str(ACCOUNT_RESTRICTED_ID)},
    )
    assert response.status_code == 403


def test_admin_import_requires_admin_and_accepts_csv() -> None:
    denied = request(
        "POST",
        "/api/v1/admin/import/csv",
        headers=SALES_HEADERS,
        files={"file": ("accounts.csv", b"name,tax_code\nExample,123", "text/csv")},
    )
    assert denied.status_code == 403

    accepted = request(
        "POST",
        "/api/v1/admin/import/csv",
        headers=ADMIN_HEADERS,
        files={"file": ("accounts.csv", b"name,tax_code\nExample,123", "text/csv")},
    )
    assert accepted.status_code == 200
    assert accepted.json()["records_received"] == 1


def test_missing_bearer_token_is_rejected() -> None:
    response = request("GET", "/api/v1/accounts/search", params={"q": "ABC"})
    assert response.status_code == 401


def test_login_locks_after_five_failed_attempts() -> None:
    payload = {"email": "lockout-check@example.com", "password": "wrong"}
    responses = [
        request("POST", "/api/v1/auth/login", json=payload)
        for _ in range(5)
    ]
    assert [response.status_code for response in responses] == [
        401,
        401,
        401,
        401,
        423,
    ]
    locked = request("POST", "/api/v1/auth/login", json=payload)
    assert locked.status_code == 423


def test_seeded_user_id_is_stable() -> None:
    login = request(
        "POST",
        "/api/v1/auth/login",
        json={"email": "sales@songnhat.com.vn", "password": "SecurePass123!"},
    )
    assert login.json()["user"]["id"] == str(SALES_USER_ID)
