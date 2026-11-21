import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import accounts, admin, auth, briefings

API_PREFIX = "/api/v1"
cors_origins = [
    origin.strip()
    for origin in os.getenv(
        "CORS_ORIGINS",
        "http://localhost:3000,http://localhost:5173",
    ).split(",")
    if origin.strip()
]

app = FastAPI(
    title="Customer 360 Briefing Assistant API",
    summary="Source-cited account briefing API for SongNhat.",
    description=(
        "OpenAPI contract and deterministic mock endpoints for frontend integration. "
        "Swagger UI is available at `/docs`; the raw OpenAPI schema is at `/openapi.json`.\n\n"
        "**Integration build:** Authentication tokens, imports, generation, persistence, "
        "and cache invalidation use in-memory mock behavior. Do not deploy this build "
        "with customer data. Replace the mock services with PostgreSQL, Redis, and the "
        "production JWT implementation before deployment.\n\n"
        "**Demo users:** `sales@songnhat.com.vn` / `SecurePass123!` and "
        "`admin@songnhat.com.vn` / `AdminPass123!`. Log in and click **Authorize** "
        "with the returned access token."
    ),
    version="0.1.0",
    openapi_tags=[
        {"name": "Authentication", "description": "Demo login and bearer token."},
        {"name": "Accounts", "description": "Scoped account search and identity matching."},
        {"name": "Briefings", "description": "Generate, retrieve, cite, and export briefings."},
        {"name": "Administration", "description": "Admin-only imports and access revocation."},
        {"name": "System", "description": "Liveness and service metadata."},
    ],
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
        "mode": "mock-integration",
    }


@app.get("/health", tags=["System"], summary="Check API liveness")
def health() -> dict[str, str]:
    return {"status": "ok"}
