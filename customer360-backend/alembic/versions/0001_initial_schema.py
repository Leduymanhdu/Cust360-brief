"""Initial Customer 360 schema.

Revision ID: 0001
Revises:
Create Date: 2026-11-21

"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

UUID_PK = sa.text("gen_random_uuid()")
NOW = sa.text("NOW()")


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto")

    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=UUID_PK, nullable=False),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("password_hash", sa.Text(), nullable=False),
        sa.Column("full_name", sa.String(255), nullable=False),
        sa.Column("role", sa.String(30), nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("TRUE"), nullable=False),
        sa.Column("failed_login_attempts", sa.Integer(), server_default=sa.text("0")),
        sa.Column("locked_until", sa.DateTime(timezone=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=NOW),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=NOW),
        sa.PrimaryKeyConstraint("id", name="pk_users"),
        sa.UniqueConstraint("email", name="uq_users_email"),
        sa.CheckConstraint("role IN ('ADMIN', 'SALES', 'SERVICE')", name="ck_users_role"),
    )

    op.create_table(
        "accounts",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=UUID_PK, nullable=False),
        sa.Column("legal_name", sa.String(500), nullable=False),
        sa.Column("tax_code", sa.String(100)),
        sa.Column("industry", sa.String(255)),
        sa.Column("status", sa.String(30), server_default=sa.text("'ACTIVE'")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=NOW),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=NOW),
        sa.PrimaryKeyConstraint("id", name="pk_accounts"),
        sa.UniqueConstraint("tax_code", name="uq_accounts_tax_code"),
        sa.CheckConstraint("status IN ('ACTIVE', 'INACTIVE')", name="ck_accounts_status"),
    )

    op.create_table(
        "sites",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=UUID_PK, nullable=False),
        sa.Column("account_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("site_name", sa.String(255), nullable=False),
        sa.Column("address", sa.Text()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=NOW),
        sa.PrimaryKeyConstraint("id", name="pk_sites"),
        sa.ForeignKeyConstraint(
            ["account_id"],
            ["accounts.id"],
            name="fk_sites_account",
            ondelete="RESTRICT",
        ),
    )

    op.create_table(
        "user_account_access",
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("account_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("granted_at", sa.DateTime(timezone=True), server_default=NOW),
        sa.PrimaryKeyConstraint("user_id", "account_id", name="pk_user_account_access"),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name="fk_access_user",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["account_id"],
            ["accounts.id"],
            name="fk_access_account",
            ondelete="CASCADE",
        ),
    )

    op.create_table(
        "crosswalk",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=UUID_PK, nullable=False),
        sa.Column("source_system", sa.String(100), nullable=False),
        sa.Column("source_account_id", sa.String(255), nullable=False),
        sa.Column("source_account_name", sa.String(500)),
        sa.Column("account_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("review_status", sa.String(30), server_default=sa.text("'PENDING'"), nullable=False),
        sa.Column("reviewed_by", postgresql.UUID(as_uuid=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=NOW),
        sa.PrimaryKeyConstraint("id", name="pk_crosswalk"),
        sa.ForeignKeyConstraint(
            ["account_id"],
            ["accounts.id"],
            name="fk_crosswalk_account",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["reviewed_by"],
            ["users.id"],
            name="fk_crosswalk_reviewer",
            ondelete="SET NULL",
        ),
        sa.UniqueConstraint(
            "source_system",
            "source_account_id",
            name="uq_crosswalk_source",
        ),
        sa.CheckConstraint(
            "review_status IN ('PENDING', 'APPROVED', 'REJECTED')",
            name="ck_crosswalk_review_status",
        ),
    )

    op.create_table(
        "commercial_records",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=UUID_PK, nullable=False),
        sa.Column("account_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("source_system", sa.String(100), nullable=False),
        sa.Column("source_record_id", sa.String(255), nullable=False),
        sa.Column("record_type", sa.String(30), nullable=False),
        sa.Column("status", sa.String(30), nullable=False),
        sa.Column("currency", sa.CHAR(3), nullable=False),
        sa.Column("total_amount", sa.Numeric(20, 2), server_default=sa.text("0"), nullable=False),
        sa.Column("record_date", sa.Date(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=NOW),
        sa.PrimaryKeyConstraint("id", name="pk_commercial_records"),
        sa.ForeignKeyConstraint(
            ["account_id"],
            ["accounts.id"],
            name="fk_commercial_account",
            ondelete="RESTRICT",
        ),
        sa.UniqueConstraint(
            "source_system",
            "source_record_id",
            name="uq_commercial_source",
        ),
        sa.CheckConstraint("record_type IN ('QUOTATION', 'ORDER')", name="ck_commercial_record_type"),
        sa.CheckConstraint("currency IN ('VND', 'USD')", name="ck_commercial_currency"),
        sa.CheckConstraint("total_amount >= 0", name="ck_commercial_amount"),
    )

    op.create_table(
        "pdf_text",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=UUID_PK, nullable=False),
        sa.Column("account_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("file_name", sa.String(500), nullable=False),
        sa.Column("file_hash", sa.String(128), nullable=False),
        sa.Column("page_number", sa.Integer()),
        sa.Column("extracted_text", sa.Text()),
        sa.Column("injection_flag", sa.Boolean(), server_default=sa.text("FALSE"), nullable=False),
        sa.Column("is_usable", sa.Boolean(), server_default=sa.text("TRUE"), nullable=False),
        sa.Column("extracted_at", sa.DateTime(timezone=True), server_default=NOW),
        sa.PrimaryKeyConstraint("id", name="pk_pdf_text"),
        sa.ForeignKeyConstraint(
            ["account_id"],
            ["accounts.id"],
            name="fk_pdf_account",
            ondelete="RESTRICT",
        ),
    )

    op.create_table(
        "briefings",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=UUID_PK, nullable=False),
        sa.Column("account_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("site_id", postgresql.UUID(as_uuid=True)),
        sa.Column("generated_by", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "briefing_status",
            sa.String(30),
            server_default=sa.text("'GENERATING'"),
            nullable=False,
        ),
        sa.Column(
            "sections",
            postgresql.JSONB(),
            server_default=sa.text("'{}'::jsonb"),
            nullable=False,
        ),
        sa.Column("is_stale", sa.Boolean(), server_default=sa.text("FALSE"), nullable=False),
        sa.Column("validation_status", sa.String(30), server_default=sa.text("'PENDING'")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=NOW),
        sa.Column("completed_at", sa.DateTime(timezone=True)),
        sa.PrimaryKeyConstraint("id", name="pk_briefings"),
        sa.ForeignKeyConstraint(
            ["account_id"],
            ["accounts.id"],
            name="fk_briefing_account",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["site_id"],
            ["sites.id"],
            name="fk_briefing_site",
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["generated_by"],
            ["users.id"],
            name="fk_briefing_user",
            ondelete="RESTRICT",
        ),
        sa.CheckConstraint(
            "briefing_status IN ('GENERATING', 'COMPLETED', 'FAILED', 'BLOCKED')",
            name="ck_briefings_status",
        ),
    )

    op.create_table(
        "citations",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=UUID_PK, nullable=False),
        sa.Column("briefing_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("citation_number", sa.Integer(), nullable=False),
        sa.Column("claim_text", sa.Text(), nullable=False),
        sa.Column("source_type", sa.String(20), nullable=False),
        sa.Column("pdf_text_id", postgresql.UUID(as_uuid=True)),
        sa.Column("commercial_record_id", postgresql.UUID(as_uuid=True)),
        sa.Column("source_excerpt", sa.Text()),
        sa.Column(
            "validation_status",
            sa.String(30),
            server_default=sa.text("'PENDING'"),
            nullable=False,
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=NOW),
        sa.PrimaryKeyConstraint("id", name="pk_citations"),
        sa.ForeignKeyConstraint(
            ["briefing_id"],
            ["briefings.id"],
            name="fk_citation_briefing",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["pdf_text_id"],
            ["pdf_text.id"],
            name="fk_citation_pdf",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["commercial_record_id"],
            ["commercial_records.id"],
            name="fk_citation_commercial",
            ondelete="RESTRICT",
        ),
        sa.UniqueConstraint(
            "briefing_id",
            "citation_number",
            name="uq_briefing_citation",
        ),
        sa.CheckConstraint("source_type IN ('PDF', 'COMMERCIAL')", name="ck_citation_source_type"),
        sa.CheckConstraint(
            "validation_status IN ('PENDING', 'VALID', 'INVALID', 'REJECTED')",
            name="ck_citation_validation_status",
        ),
        sa.CheckConstraint(
            "(source_type = 'PDF' AND pdf_text_id IS NOT NULL AND commercial_record_id IS NULL) "
            "OR (source_type = 'COMMERCIAL' AND commercial_record_id IS NOT NULL "
            "AND pdf_text_id IS NULL)",
            name="ck_citation_source",
        ),
    )

    op.create_table(
        "audit_logs",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=UUID_PK, nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True)),
        sa.Column("action", sa.String(100), nullable=False),
        sa.Column("resource_type", sa.String(50)),
        sa.Column("resource_id", postgresql.UUID(as_uuid=True)),
        sa.Column("ip_address", postgresql.INET()),
        sa.Column(
            "metadata",
            postgresql.JSONB(),
            server_default=sa.text("'{}'::jsonb"),
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=NOW),
        sa.PrimaryKeyConstraint("id", name="pk_audit_logs"),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name="fk_audit_user",
            ondelete="SET NULL",
        ),
    )

    op.create_table(
        "import_jobs",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=UUID_PK, nullable=False),
        sa.Column("uploaded_by", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("file_kind", sa.String(10), nullable=False),
        sa.Column("file_name", sa.String(500), nullable=False),
        sa.Column("content_type", sa.String(150), nullable=False),
        sa.Column("storage_path", sa.String(1000), nullable=False),
        sa.Column("size_bytes", sa.BigInteger(), nullable=False),
        sa.Column("checksum_sha256", sa.CHAR(64), nullable=False),
        sa.Column("status", sa.String(30), server_default=sa.text("'PENDING'"), nullable=False),
        sa.Column("records_received", sa.Integer(), server_default=sa.text("0"), nullable=False),
        sa.Column(
            "warnings",
            postgresql.JSONB(),
            server_default=sa.text("'[]'::jsonb"),
            nullable=False,
        ),
        sa.Column("error_message", sa.Text()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=NOW),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=NOW),
        sa.Column("completed_at", sa.DateTime(timezone=True)),
        sa.PrimaryKeyConstraint("id", name="pk_import_jobs"),
        sa.ForeignKeyConstraint(
            ["uploaded_by"],
            ["users.id"],
            name="fk_import_user",
            ondelete="RESTRICT",
        ),
        sa.CheckConstraint("file_kind IN ('CSV', 'PDF')", name="ck_import_jobs_file_kind"),
        sa.CheckConstraint(
            "status IN ('PENDING', 'PROCESSING', 'COMPLETED', 'FAILED')",
            name="ck_import_jobs_status",
        ),
        sa.CheckConstraint("size_bytes >= 0", name="ck_import_jobs_size_bytes"),
        sa.CheckConstraint("records_received >= 0", name="ck_import_jobs_records_received"),
    )

    op.create_index(
        "idx_accounts_legal_name",
        "accounts",
        [sa.text("to_tsvector('simple', legal_name)")],
        postgresql_using="gin",
    )
    op.create_index(
        "idx_commercial_account_date",
        "commercial_records",
        ["account_id", "record_date"],
    )
    op.create_index("idx_pdf_account", "pdf_text", ["account_id"])
    op.create_index("idx_pdf_hash", "pdf_text", ["file_hash"])
    op.create_index(
        "idx_briefings_account_date",
        "briefings",
        ["account_id", sa.text("created_at DESC")],
    )
    op.create_index("idx_citations_briefing", "citations", ["briefing_id"])
    op.create_index(
        "idx_audit_user_date",
        "audit_logs",
        ["user_id", sa.text("created_at DESC")],
    )
    op.create_index(
        "idx_import_jobs_status",
        "import_jobs",
        ["status", sa.text("created_at DESC")],
    )
    op.create_index(
        "idx_import_jobs_user",
        "import_jobs",
        ["uploaded_by", sa.text("created_at DESC")],
    )
    op.create_index("idx_import_jobs_checksum", "import_jobs", ["checksum_sha256"])


def downgrade() -> None:
    op.drop_index("idx_import_jobs_checksum", table_name="import_jobs")
    op.drop_index("idx_import_jobs_user", table_name="import_jobs")
    op.drop_index("idx_import_jobs_status", table_name="import_jobs")
    op.drop_index("idx_audit_user_date", table_name="audit_logs")
    op.drop_index("idx_citations_briefing", table_name="citations")
    op.drop_index("idx_briefings_account_date", table_name="briefings")
    op.drop_index("idx_pdf_hash", table_name="pdf_text")
    op.drop_index("idx_pdf_account", table_name="pdf_text")
    op.drop_index("idx_commercial_account_date", table_name="commercial_records")
    op.drop_index("idx_accounts_legal_name", table_name="accounts")

    op.drop_table("import_jobs")
    op.drop_table("audit_logs")
    op.drop_table("citations")
    op.drop_table("briefings")
    op.drop_table("pdf_text")
    op.drop_table("commercial_records")
    op.drop_table("crosswalk")
    op.drop_table("user_account_access")
    op.drop_table("sites")
    op.drop_table("accounts")
    op.drop_table("users")
    # pgcrypto is left in place because other schemas may rely on it.
