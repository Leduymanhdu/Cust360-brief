"""Build and persist source-linked briefings from PostgreSQL records."""

from collections import defaultdict
from datetime import datetime, timezone
from decimal import Decimal
from uuid import UUID, uuid4

from psycopg import Connection
from psycopg.types.json import Jsonb


def create_briefing(
    connection: Connection,
    account_id: UUID,
    site_id: UUID | None,
    generated_by: UUID,
) -> UUID:
    with connection.transaction():
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT id, legal_name, tax_code, industry
                FROM accounts
                WHERE id = %s
                """,
                (account_id,),
            )
            account = cursor.fetchone()
            if account is None:
                raise ValueError("Account not found.")

            site = None
            if site_id is not None:
                cursor.execute(
                    """
                    SELECT id, site_name, address
                    FROM sites
                    WHERE id = %s AND account_id = %s
                    """,
                    (site_id, account_id),
                )
                site = cursor.fetchone()
                if site is None:
                    raise ValueError("Site not found for this account.")

            cursor.execute(
                """
                SELECT id, file_name, page_number, extracted_text
                FROM pdf_text
                WHERE account_id = %s
                  AND is_usable = TRUE
                  AND injection_flag = FALSE
                  AND NULLIF(BTRIM(extracted_text), '') IS NOT NULL
                ORDER BY extracted_at DESC, id
                """,
                (account_id,),
            )
            pdf_sources = cursor.fetchall()

            cursor.execute(
                """
                SELECT id, source_record_id, record_type, status, currency,
                       total_amount, record_date
                FROM commercial_records
                WHERE account_id = %s
                ORDER BY record_date DESC, id
                """,
                (account_id,),
            )
            commercial_sources = cursor.fetchall()

            sections, citations = _build_sections(
                account=account,
                site=site,
                pdf_sources=pdf_sources,
                commercial_sources=commercial_sources,
            )

            briefing_id = uuid4()
            created_at = datetime.now(timezone.utc)
            cursor.execute(
                """
                INSERT INTO briefings (
                    id, account_id, site_id, generated_by, briefing_status,
                    sections, is_stale, validation_status, created_at, completed_at
                )
                VALUES (%s, %s, %s, %s, 'COMPLETED', %s, FALSE, 'PENDING', %s, %s)
                """,
                (
                    briefing_id,
                    account_id,
                    site_id,
                    generated_by,
                    Jsonb(sections),
                    created_at,
                    created_at,
                ),
            )
            for citation in citations:
                cursor.execute(
                    """
                    INSERT INTO citations (
                        briefing_id, citation_number, claim_text, source_type,
                        pdf_text_id, commercial_record_id, source_excerpt,
                        validation_status
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, 'PENDING')
                    """,
                    (
                        briefing_id,
                        citation["citation_number"],
                        citation["claim_text"],
                        citation["source_type"],
                        citation.get("pdf_text_id"),
                        citation.get("commercial_record_id"),
                        citation["source_excerpt"],
                    ),
                )

    return briefing_id


def _build_sections(
    *,
    account: dict,
    site: dict | None,
    pdf_sources: list[dict],
    commercial_sources: list[dict],
) -> tuple[dict, list[dict]]:
    citations: list[dict] = []
    pdf_citation_numbers: list[int] = []
    for source in pdf_sources:
        citation_number = len(citations) + 1
        excerpt = source["extracted_text"][:1000]
        citations.append(
            {
                "citation_number": citation_number,
                "claim_text": f"Extracted text from {source['file_name']}.",
                "source_type": "PDF",
                "pdf_text_id": source["id"],
                "source_excerpt": excerpt,
            }
        )
        pdf_citation_numbers.append(citation_number)

    commercial_citation_numbers: list[int] = []
    totals: dict[tuple[str, str], Decimal] = defaultdict(Decimal)
    record_counts: dict[tuple[str, str], int] = defaultdict(int)
    for source in commercial_sources:
        key = (source["record_type"], source["currency"])
        totals[key] += source["total_amount"]
        record_counts[key] += 1
        citation_number = len(citations) + 1
        excerpt = (
            f"{source['source_record_id']} | {source['record_type']} | "
            f"{source['status']} | {source['currency']} "
            f"{source['total_amount']:,.2f} | {source['record_date'].isoformat()}"
        )
        citations.append(
            {
                "citation_number": citation_number,
                "claim_text": excerpt,
                "source_type": "COMMERCIAL",
                "commercial_record_id": source["id"],
                "source_excerpt": excerpt,
            }
        )
        commercial_citation_numbers.append(citation_number)

    account_location = account["legal_name"]
    if site:
        account_location += f" - {site['site_name']}"
        if site["address"]:
            account_location += f" ({site['address']})"
    elif account["tax_code"]:
        account_location += f" (tax code: {account['tax_code']})"

    if pdf_sources:
        pdf_summary = "Available source documents: " + "; ".join(
            f"{source['file_name']}"
            + (
                f", page {source['page_number']}"
                if source["page_number"] is not None
                else ""
            )
            for source in pdf_sources
        )
    else:
        pdf_summary = "No usable PDF source documents are available."

    if totals:
        commercial_summary = "; ".join(
            f"{record_counts[(record_type, currency)]} {record_type.lower()} "
            f"record(s), total {currency} {total:,.2f}"
            for (record_type, currency), total in sorted(totals.items())
        )
    else:
        commercial_summary = "No commercial records are available."

    sections = {
        "account_and_site": {
            "content": account_location,
            "citations": [],
        },
        "contacts_and_roles": {
            "content": "Contact and role records are not included in the current database schema.",
            "citations": [],
        },
        "recent_interactions": {
            "content": (
                "The database has no structured interaction table. "
                + pdf_summary
            ),
            "citations": pdf_citation_numbers,
        },
        "commercial_facts": {
            "content": commercial_summary,
            "citations": commercial_citation_numbers,
        },
        "service_issues": {
            "content": "Service issue records are not included in the current database schema.",
            "citations": [],
        },
        "suggested_questions_and_gaps": {
            "content": (
                "Confirm the current account contacts and any service issues; "
                "those records are not available in the current database schema."
            ),
            "citations": [],
        },
    }
    return sections, citations
