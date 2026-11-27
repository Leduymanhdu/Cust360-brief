# Customer 360 Backend

## Local API

From this directory, start the database and API:

```powershell
docker compose up -d postgres
docker compose up --build -d api
```

The API is available at `http://localhost:8000`; OpenAPI documentation is at
`http://localhost:8000/docs`. PostgreSQL is configured with the local Compose
credentials in `docker-compose.yml`. The database schema is initialized from
`database/init.sql`; load `database/seed.sql` separately when the database has
no application data.

Run the seed once against an empty initialized database:

```powershell
docker compose cp .\database\seed.sql postgres:/tmp/seed.sql
docker compose exec postgres psql -U customer360 -d customer360 -1 -v ON_ERROR_STOP=1 -f /tmp/seed.sql
```

The seed inserts are not idempotent; do not run the seed a second time.

The seed user credentials are `sales@cust360.vn` / `password123` and
`admin@cust360.vn` / `password123`. Override `JWT_SECRET_KEY` outside local
development.

## Account and briefing endpoints

- `POST /api/v1/auth/login` authenticates a database user and returns a JWT.
- `GET /api/v1/accounts/search?q=...` searches visible account names and tax codes.
- `GET /api/v1/accounts/{account_id}` returns account details and sites.
- `POST /api/v1/briefings/generate` creates and persists a six-section briefing.
- `GET /api/v1/briefings/{briefing_id}` returns a saved briefing.
- `GET /api/v1/briefings/{briefing_id}/citations` returns its source citations.

Briefing generation is deterministic and uses usable PDF text and commercial
records currently present in PostgreSQL; it does not call an AI provider.