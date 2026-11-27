import asyncio
import os
from collections.abc import Iterator
from pathlib import Path
from typing import Any
from uuid import UUID, uuid4

import bcrypt
import httpx
import psycopg
import pytest
from psycopg.rows import dict_row
from psycopg.types.json import Jsonb

from app.database import get_db_connection
from app.main import app

JWT_SECRET = "test-customer360-jwt-secret-key-at-least-32-characters"
TEST_PASSWORD = "Password123!"
TEST_PASSWORD_HASH = bcrypt.hashpw(
    TEST_PASSWORD.encode("utf-8"),
    bcrypt.gensalt(),
).decode("utf-8")


def request(method: str, path: str, **kwargs: Any) -> httpx.Response:
    async def send() -> httpx.Response:
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app),
            base_url="http://test",
        ) as client:
            return await client.request(method, path, **kwargs)

    return asyncio.run(send())


@pytest.fixture
def api_data(monkeypatch: pytest.MonkeyPatch) -> Iterator[dict[str, UUID]]:
    database_url = os.getenv("TEST_DATABASE_URL")
    if not database_url:
        pytest.skip("Set TEST_DATABASE_URL to run PostgreSQL API integration tests.")

    monkeypatch.setenv("JWT_SECRET_KEY", JWT_SECRET)
    connection = psycopg.connect(
        database_url,
        autocommit=False,
        row_factory=dict_row,
    )
    ids = {
        key: uuid4()
        for key in (
            "admin_id",
            "sales_id",
            "account_id",
            "second_account_id",
            "restricted_account_id",
            "site_id",
            "briefing_id",
            "pdf_id",
            "injection_pdf_id",
            "commercial_id",
            "second_commercial_id",
        )
    }

    sections = {
        key: {"content": "Fixture content.", "citations": []}
        for key in (
            "account_and_site",
            "contacts_and_roles",
            "recent_interactions",
            "commercial_facts",
            "service_issues",
            "suggested_questions_and_gaps",
        )
    }
    try:
        with connection.cursor() as cursor:
            cursor.executemany(
                """
                INSERT INTO users (id, email, password_hash, full_name, role)
                VALUES (%s, %s, %s, %s, %s)
                """,
                [
                    (
                        ids["admin_id"],
                        "admin@example.com",
                        TEST_PASSWORD_HASH,
                        "Test Administrator",
                        "ADMIN",
                    ),
                    (
                        ids["sales_id"],
                        "sales@example.com",
                        TEST_PASSWORD_HASH,
                        "Test Sales",
                        "SALES",
                    ),
                ],
            )
            cursor.executemany(
                """
                INSERT INTO accounts (id, legal_name, tax_code, industry, status)
                VALUES (%s, %s, %s, %s, 'ACTIVE')
                """,
                [
                    (
                        ids["account_id"],
                        "An Phat Telecom",
                        "0101111222",
                        "Telecommunications",
                    ),
                    (
                        ids["second_account_id"],
                        "An Phat Industries",
                        "0101111333",
                        "Manufacturing",
                    ),
                    (
                        ids["restricted_account_id"],
                        "An Phat Restricted",
                        "0101111444",
                        "Manufacturing",
                    ),
                ],
            )
            cursor.executemany(
                """
                INSERT INTO user_account_access (user_id, account_id)
                VALUES (%s, %s)
                """,
                [
                    (ids["sales_id"], ids["account_id"]),
                    (ids["sales_id"], ids["second_account_id"]),
                ],
            )
            cursor.execute(
                """
                INSERT INTO sites (id, account_id, site_name, address)
                VALUES (%s, %s, 'Hanoi Office', '18 Pham Hung')
                """,
                (ids["site_id"], ids["account_id"]),
            )
            cursor.executemany(
                """
                INSERT INTO commercial_records (
                    id, account_id, source_system, source_record_id, record_type,
                    status, currency, total_amount, record_date
                )
                VALUES (%s, %s, 'TEST', %s, 'ORDER', 'COMPLETED', 'VND', %s, CURRENT_DATE)
                """,
                [
                    (ids["commercial_id"], ids["account_id"], "ORDER-1", 15_000_000_000),
                    (
                        ids["second_commercial_id"],
                        ids["account_id"],
                        "ORDER-2",
                        30_200_000_000,
                    ),
                ],
            )
            cursor.executemany(
                """
                INSERT INTO pdf_text (
                    id, account_id, file_name, file_hash, page_number,
                    extracted_text, injection_flag, is_usable
                )
                VALUES (%s, %s, %s, %s, 1, %s, %s, %s)
                """,
                [
                    (
                        ids["pdf_id"],
                        ids["account_id"],
                        "safe.pdf",
                        f"hash-{ids['pdf_id']}",
                        "A verified source excerpt.",
                        False,
                        True,
                    ),
                    (
                        ids["injection_pdf_id"],
                        ids["account_id"],
                        "unusable.pdf",
                        f"hash-{ids['injection_pdf_id']}",
                        "Untrusted text.",
                        True,
                        False,
                    ),
                ],
            )
            cursor.execute(
                """
                INSERT INTO briefings (
                    id, account_id, site_id, generated_by, briefing_status,
                    sections, validation_status, created_at, completed_at
                )
                VALUES (%s, %s, %s, %s, 'COMPLETED', %s, 'PASSED', NOW(), NOW())
                """,
                (
                    ids["briefing_id"],
                    ids["account_id"],
                    ids["site_id"],
                    ids["sales_id"],
                    Jsonb(sections),
                ),
            )
            cursor.executemany(
                """
                INSERT INTO citations (
                    briefing_id, citation_number, claim_text, source_type,
                    pdf_text_id, commercial_record_id, source_excerpt,
                    validation_status
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, 'VALID')
                """,
                [
                    (
                        ids["briefing_id"],
                        1,
                        "A verified source claim.",
                        "PDF",
                        ids["pdf_id"],
                        None,
                        "A verified source excerpt.",
                    ),
                    (
                        ids["briefing_id"],
                        2,
                        "A completed order.",
                        "COMMERCIAL",
                        None,
                        ids["commercial_id"],
                        "ORDER-1 | ORDER | COMPLETED | VND 15,000,000,000",
                    ),
                ],
            )

        app.dependency_overrides[get_db_connection] = lambda: connection
        yield ids
    finally:
        app.dependency_overrides.pop(get_db_connection, None)
        connection.rollback()
        connection.close()


@pytest.fixture
def seeded_api(monkeypatch: pytest.MonkeyPatch) -> Iterator[None]:
    database_url = os.getenv("TEST_DATABASE_URL")
    if not database_url:
        pytest.skip("Set TEST_DATABASE_URL to run PostgreSQL API integration tests.")

    monkeypatch.setenv("JWT_SECRET_KEY", JWT_SECRET)
    connection = psycopg.connect(
        database_url,
        autocommit=False,
        row_factory=dict_row,
    )
    seed_path = Path(__file__).resolve().parents[1] / "database" / "seed.sql"
    try:
        with connection.cursor() as cursor:
            cursor.execute(seed_path.read_text(encoding="utf-8"), prepare=False)
        app.dependency_overrides[get_db_connection] = lambda: connection
        yield
    finally:
        app.dependency_overrides.pop(get_db_connection, None)
        connection.rollback()
        connection.close()


def login(email: str = "sales@example.com") -> dict[str, str]:
    response = request(
        "POST",
        "/api/v1/auth/login",
        json={"email": email, "password": TEST_PASSWORD},
    )
    assert response.status_code == 200
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def test_openapi_documents_database_account_and_briefing_contract() -> None:
    response = request("GET", "/openapi.json")
    assert response.status_code == 200
    document = response.json()
    assert "/api/v1/accounts/search" in document["paths"]
    assert "/api/v1/accounts/{account_id}" in document["paths"]
    assert "/api/v1/accounts/{account_id}/briefings/latest" in document["paths"]
    assert "/api/v1/briefings/generate" in document["paths"]
    assert "/api/v1/briefings/{briefing_id}/citations" in document["paths"]
    assert document["paths"]["/api/v1/accounts/{account_id}"]["get"]["security"] == [
        {"BearerAuth": []}
    ]


def test_login_search_uses_database_scope_and_match_status(api_data: dict[str, UUID]) -> None:
    headers = login()
    scoped = request(
        "GET",
        "/api/v1/accounts/search",
        headers=headers,
    )
    assert scoped.status_code == 200
    assert {row["id"] for row in scoped.json()["results"]} == {
        str(api_data["account_id"]),
        str(api_data["second_account_id"]),
    }

    ambiguous = request(
        "GET",
        "/api/v1/accounts/search",
        params={"q": "An Phat"},
        headers=headers,
    )
    assert ambiguous.status_code == 200
    body = ambiguous.json()
    assert {row["id"] for row in body["results"]} == {
        str(api_data["account_id"]),
        str(api_data["second_account_id"]),
    }
    assert body["requires_manual_selection"] is True
    assert {row["match_status"] for row in body["results"]} == {"AMBIGUOUS"}

    exact = request(
        "GET",
        "/api/v1/accounts/search",
        params={"q": "0101111222"},
        headers=headers,
    )
    assert exact.status_code == 200
    assert exact.json()["results"][0]["match_status"] == "EXACT"


def test_latest_briefing_checks_account_scope_and_missing_data(
    api_data: dict[str, UUID],
) -> None:
    headers = login()
    latest = request(
        "GET",
        f"/api/v1/accounts/{api_data['account_id']}/briefings/latest",
        headers=headers,
    )
    assert latest.status_code == 200
    assert latest.json()["briefing_id"] == str(api_data["briefing_id"])

    missing = request(
        "GET",
        f"/api/v1/accounts/{api_data['second_account_id']}/briefings/latest",
        headers=headers,
    )
    assert missing.status_code == 404

    forbidden = request(
        "GET",
        f"/api/v1/accounts/{api_data['restricted_account_id']}/briefings/latest",
        headers=headers,
    )
    assert forbidden.status_code == 403


def test_account_detail_checks_scope_and_not_found(api_data: dict[str, UUID]) -> None:
    headers = login()
    detail = request(
        "GET",
        f"/api/v1/accounts/{api_data['account_id']}",
        headers=headers,
    )
    assert detail.status_code == 200
    assert detail.json()["sites"][0]["id"] == str(api_data["site_id"])

    forbidden = request(
        "GET",
        f"/api/v1/accounts/{api_data['restricted_account_id']}",
        headers=headers,
    )
    assert forbidden.status_code == 403

    missing = request(
        "GET",
        f"/api/v1/accounts/{uuid4()}",
        headers=headers,
    )
    assert missing.status_code == 404

    admin_headers = login("admin@example.com")
    admin_detail = request(
        "GET",
        f"/api/v1/accounts/{api_data['restricted_account_id']}",
        headers=admin_headers,
    )
    assert admin_detail.status_code == 200


def test_get_briefing_and_citations_reads_database_sources(
    api_data: dict[str, UUID],
) -> None:
    headers = login()
    briefing = request(
        "GET",
        f"/api/v1/briefings/{api_data['briefing_id']}",
        headers=headers,
    )
    assert briefing.status_code == 200
    assert briefing.json()["status"] == "COMPLETED"
    assert len(briefing.json()["sections"]) == 6

    citations = request(
        "GET",
        f"/api/v1/briefings/{api_data['briefing_id']}/citations",
        headers=headers,
    )
    assert citations.status_code == 200
    items = citations.json()["citations"]
    assert [item["citation_number"] for item in items] == [1, 2]
    assert items[0]["source_id"] == str(api_data["pdf_id"])
    assert items[0]["page_number"] == 1
    assert items[1]["source_id"] == str(api_data["commercial_id"])
    assert items[1]["page_number"] is None

    export = request(
        "GET",
        f"/api/v1/briefings/{api_data['briefing_id']}/export",
        headers=headers,
    )
    assert export.status_code == 200
    assert export.headers["content-type"] == "application/pdf"
    assert export.content.startswith(b"%PDF-1.4")


def test_generate_briefing_persists_sections_and_safe_citations(
    api_data: dict[str, UUID],
) -> None:
    headers = login()
    accepted = request(
        "POST",
        "/api/v1/briefings/generate",
        headers=headers,
        json={
            "account_id": str(api_data["account_id"]),
            "site_id": str(api_data["site_id"]),
        },
    )
    assert accepted.status_code == 202
    assert accepted.json()["status"] == "GENERATING"

    briefing_id = accepted.json()["briefing_id"]
    briefing = request(
        "GET",
        f"/api/v1/briefings/{briefing_id}",
        headers=headers,
    )
    assert briefing.status_code == 200
    assert briefing.json()["status"] == "COMPLETED"
    assert briefing.json()["validation_status"] == "PENDING"
    assert set(briefing.json()["sections"]) == {
        "account_and_site",
        "contacts_and_roles",
        "recent_interactions",
        "commercial_facts",
        "service_issues",
        "suggested_questions_and_gaps",
    }
    assert "45,200,000,000.00" in briefing.json()["sections"]["commercial_facts"]["content"]

    citations = request(
        "GET",
        f"/api/v1/briefings/{briefing_id}/citations",
        headers=headers,
    )
    items = citations.json()["citations"]
    assert len(items) == 3
    assert {item["source_id"] for item in items} == {
        str(api_data["pdf_id"]),
        str(api_data["commercial_id"]),
        str(api_data["second_commercial_id"]),
    }
    assert all(item["source_id"] != str(api_data["injection_pdf_id"]) for item in items)


def test_generate_briefing_returns_not_found_and_scope_errors(
    api_data: dict[str, UUID],
) -> None:
    headers = login()
    forbidden = request(
        "POST",
        "/api/v1/briefings/generate",
        headers=headers,
        json={"account_id": str(api_data["restricted_account_id"])},
    )
    assert forbidden.status_code == 403

    missing = request(
        "POST",
        "/api/v1/briefings/generate",
        headers=headers,
        json={"account_id": str(uuid4())},
    )
    assert missing.status_code == 404

    invalid_site = request(
        "POST",
        "/api/v1/briefings/generate",
        headers=headers,
        json={
            "account_id": str(api_data["account_id"]),
            "site_id": str(uuid4()),
        },
    )
    assert invalid_site.status_code == 404


def test_admin_revokes_database_scope(api_data: dict[str, UUID]) -> None:
    sales_headers = login()
    admin_headers = login("admin@example.com")
    response = request(
        "POST",
        f"/api/v1/admin/users/{api_data['sales_id']}/revoke-access",
        headers=admin_headers,
        json={
            "account_id": str(api_data["account_id"]),
            "reason": "Test access revocation",
        },
    )
    assert response.status_code == 200
    assert response.json()["revoked"] is True
    assert response.json()["cache_cleared"] is False

    account = request(
        "GET",
        f"/api/v1/accounts/{api_data['account_id']}",
        headers=sales_headers,
    )
    assert account.status_code == 403


def test_admin_import_still_uses_database_role(api_data: dict[str, UUID]) -> None:
    sales_response = request(
        "POST",
        "/api/v1/admin/import/csv",
        headers=login(),
        files={"file": ("accounts.csv", b"name,tax_code\nExample,123", "text/csv")},
    )
    assert sales_response.status_code == 403

    admin_response = request(
        "POST",
        "/api/v1/admin/import/csv",
        headers=login("admin@example.com"),
        files={"file": ("accounts.csv", b"name,tax_code\nExample,123", "text/csv")},
    )
    assert admin_response.status_code == 200


@pytest.mark.usefixtures("api_data")
def test_missing_bearer_token_is_rejected() -> None:
    response = request(
        "GET",
        "/api/v1/accounts/search",
        params={"q": "An Phat"},
    )
    assert response.status_code == 401


@pytest.mark.usefixtures("api_data")
def test_login_rejects_bad_password_and_locks_account() -> None:
    attempts = [
        request(
            "POST",
            "/api/v1/auth/login",
            json={"email": "sales@example.com", "password": "wrong"},
        ).status_code
        for _ in range(5)
    ]
    assert attempts == [401, 401, 401, 401, 423]


def test_database_connection_errors_return_service_unavailable() -> None:
    def database_offline() -> None:
        raise psycopg.OperationalError("database unavailable")

    app.dependency_overrides[get_db_connection] = database_offline
    try:
        response = request(
            "GET",
            "/api/v1/accounts/search",
            params={"q": "An Phat"},
            headers={"Authorization": "Bearer invalid"},
        )
    finally:
        app.dependency_overrides.pop(get_db_connection, None)

    assert response.status_code == 503
    assert response.json()["code"] == "DATABASE_UNAVAILABLE"


def test_seeded_account_briefing_and_citations_match_contract(
    seeded_api: None,
) -> None:
    response = request(
        "POST",
        "/api/v1/auth/login",
        json={"email": "sales@cust360.vn", "password": "password123"},
    )
    assert response.status_code == 200
    headers = {"Authorization": f"Bearer {response.json()['access_token']}"}

    account_search = request(
        "GET",
        "/api/v1/accounts/search",
        params={"q": "An Phát"},
        headers=headers,
    )
    assert account_search.status_code == 200
    assert len(account_search.json()["results"]) == 1
    account_id = account_search.json()["results"][0]["id"]

    scoped_accounts = request(
        "GET",
        "/api/v1/accounts/search",
        headers=headers,
    )
    assert scoped_accounts.status_code == 200
    assert len(scoped_accounts.json()["results"]) == 4

    briefing_id = "eeeeeeee-eeee-eeee-eeee-eeeeeeeeeee1"
    briefing = request(
        "GET",
        f"/api/v1/briefings/{briefing_id}",
        headers=headers,
    )
    assert briefing.status_code == 200
    assert briefing.json()["account_id"] == account_id
    assert len(briefing.json()["sections"]) == 6

    citations = request(
        "GET",
        f"/api/v1/briefings/{briefing_id}/citations",
        headers=headers,
    )
    items = citations.json()["citations"]
    assert citations.status_code == 200
    assert [item["citation_number"] for item in items] == [1, 2, 3]
    assert [item["source_type"] for item in items] == [
        "COMMERCIAL",
        "COMMERCIAL",
        "PDF",
    ]

    latest = request(
        "GET",
        f"/api/v1/accounts/{account_id}/briefings/latest",
        headers=headers,
    )
    assert latest.status_code == 200
    assert latest.json()["briefing_id"] == briefing_id
