"""PostgreSQL connection dependency for API requests."""

import os
from collections.abc import Iterator

import psycopg
from fastapi import HTTPException, status
from psycopg.rows import dict_row


def get_db_connection() -> Iterator[psycopg.Connection]:
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database connection is not configured.",
        )

    connection = psycopg.connect(
        database_url,
        autocommit=True,
        row_factory=dict_row,
    )
    try:
        yield connection
    finally:
        connection.close()
