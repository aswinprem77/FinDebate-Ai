# StockDebate.AI

StockDebate.AI is a web application for generating structured stock analysis from multiple model perspectives. The current codebase contains the initial application foundation: authentication, PostgreSQL-backed users, and a mock market evidence endpoint for the first supported ticker.

## Status

Implemented modules:

- Module 1: Project setup and authentication
- Module 2: Market evidence package and cache skeleton
- Module 3: Rate limiter
- Module 4: Three-model debate engine using mocked analyst models

The market data and debate flows currently use mock data for `AAPL`. Live market API and LLM provider integrations are planned for later modules.

## Tech Stack

- Backend: FastAPI, Pydantic, SQLAlchemy
- Database: PostgreSQL
- Cache: Redis when configured, in-memory fallback otherwise
- Frontend: React, Vite, Tailwind CSS

## Project Structure

```text
backend/
  app/
    api/          FastAPI route handlers and dependencies
    core/         Configuration, feature flags, security helpers
    data/         Mock market data
    db/           SQLAlchemy database setup and tables
    models/       Domain models
    schemas/      API request and response schemas
    services/     Application services
    prompts/      Debate role prompt templates
frontend/
  src/
    api/          Frontend API client
    App.jsx       Application shell
```

## Backend Setup

Create a virtual environment and install dependencies:

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Create `backend/.env`:

```env
DATABASE_URL=postgresql://postgres:12341@localhost:5432/stockdebate
CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
JWT_SECRET=change-this-before-deployment
EVIDENCE_CACHE_TTL_SECONDS=900
```

Optional Redis cache:

```env
REDIS_URL=redis://localhost:6379/0
```

Run the backend:

```powershell
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Health check:

```text
http://127.0.0.1:8000/api/v1/health
```

## Frontend Setup

Install dependencies:

```powershell
cd frontend
npm install
```

Run the frontend:

```powershell
npm run dev
```

Open:

```text
http://127.0.0.1:5173
```

## API Endpoints

Authentication:

- `POST /api/v1/auth/register`
- `POST /api/v1/auth/login`
- `GET /api/v1/auth/me`
- `PATCH /api/v1/auth/me/tier`

Market evidence:

- `GET /api/v1/market/evidence/AAPL`

Debate:

- `POST /api/v1/debate/AAPL`

The market evidence and debate endpoints require a bearer token from the login or register response.

## Debate Engine

Module 4 runs three analyst roles in parallel against the same evidence package:

- Model A: fundamental analyst
- Model B: technical analyst
- Model C: macro and sentiment strategist

Outputs are returned as structured JSON. The current implementation uses deterministic mock analysts so the rest of the product can be built before real LLM provider credentials are added.

## Rate Limiting

Module 3 applies debate-style quotas to protected evidence and debate endpoints.

Current quotas:

- Newbie and intermediate users: 5 requests per hour, 20 requests per day
- Pro users: 30 requests per hour, no daily cap
- Admin users: unlimited

Rate limit responses include `X-RateLimit-*` headers. Limit hits are logged to PostgreSQL in the `rate_limit_events` table when PostgreSQL is configured.

## Notes

- `backend/.env` is ignored by Git and should not be committed.
- The backend creates the initial `users` table automatically on startup.
- If `REDIS_URL` is not configured or Redis is unavailable, evidence caching uses an in-memory fallback.
