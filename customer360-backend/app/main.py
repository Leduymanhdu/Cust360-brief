import logging
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from psycopg import Error as PsycopgError
from psycopg import IntegrityError, OperationalError

from app.routers import accounts, admin, auth, briefings

API_PREFIX = "/api/v1"
logger = logging.getLogger(__name__)
cors_origins = [
    origin.strip()
    for origin in os.getenv(
        "CORS_ORIGINS",
        "http://localhost:3000,http://localhost:5173,"
        "http://127.0.0.1:3000,http://127.0.0.1:5173,http://127.0.0.1:5000",
    ).split(",")
    if origin.strip()
]

app = FastAPI(
    title="Customer 360 Briefing Assistant API",
    summary="Source-cited account briefing API for SongNhat.",
    description=(
        "Account search/details, login, account scope, and briefing persistence use "
        "PostgreSQL. Briefing content is assembled deterministically from available "
        "account, PDF, and commercial records; it does not call an AI provider. "
        "CSV/PDF imports remain integration stubs. Swagger UI is available at `/docs`."
    ),
    version="0.1.0",
    openapi_tags=[
        {"name": "Authentication", "description": "Database login and short-lived JWT bearer tokens."},
        {"name": "Accounts", "description": "Scoped account search and identity matching."},
        {"name": "Briefings", "description": "Generate, retrieve, cite, and export briefings."},
        {"name": "Administration", "description": "Admin-only imports and access revocation."},
        {"name": "System", "description": "Liveness and service metadata."},
    ],
)


@app.exception_handler(OperationalError)
async def handle_database_unavailable(_request, exc: OperationalError) -> JSONResponse:
    logger.error(
        "PostgreSQL connection failed: %s",
        exc,
        exc_info=(type(exc), exc, exc.__traceback__),
    )
    return JSONResponse(
        status_code=503,
        content={
            "detail": "Database is unavailable.",
            "code": "DATABASE_UNAVAILABLE",
        },
    )


@app.exception_handler(IntegrityError)
async def handle_database_conflict(_request, exc: IntegrityError) -> JSONResponse:
    logger.error(
        "PostgreSQL rejected a conflicting write: %s",
        exc,
        exc_info=(type(exc), exc, exc.__traceback__),
    )
    return JSONResponse(
        status_code=409,
        content={
            "detail": "The requested data conflicts with an existing record.",
            "code": "DATABASE_CONFLICT",
        },
    )


@app.exception_handler(PsycopgError)
async def handle_database_error(_request, exc: PsycopgError) -> JSONResponse:
    logger.error(
        "PostgreSQL query failed: %s",
        exc,
        exc_info=(type(exc), exc, exc.__traceback__),
    )
    return JSONResponse(
        status_code=500,
        content={
            "detail": "A database operation failed.",
            "code": "DATABASE_ERROR",
        },
    )


app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["Authorization", "Content-Type"],
)

app.include_router(auth.router, prefix=API_PREFIX)
app.include_router(accounts.router, prefix=API_PREFIX)
app.include_router(briefings.router, prefix=API_PREFIX)
app.include_router(admin.router, prefix=API_PREFIX)


@app.get("/", tags=["System"], summary="API service information")
def root() -> dict[str, str]:
    return {
        "service": "Customer 360 Briefing Assistant API",
        "version": app.version,
        "docs_url": "/docs",
        "openapi_url": "/openapi.json",
        "mode": "postgresql",
    }


@app.get("/health", tags=["System"], summary="Check API liveness")
def health() -> dict[str, str]:
    return {"status": "ok"}
