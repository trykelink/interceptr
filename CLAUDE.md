# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

# Interceptr — Claude Code Memory

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What is this project
Interceptr is the first product by Kelink (kelink.dev) — an open source AI agent security 
middleware. It acts as a proxy between AI agents and their tools, intercepting every action 
before it executes. The core principle: nothing runs without inspection.

## Current status
- ✅ Week 1: Audit Logging — COMPLETE
- ⏳ Week 2: Tool Call Interceptor
- ⏳ Week 3: Policy Engine with YAML
- ⏳ Week 4: Prompt Injection Detection
- ⏳ Week 5: Docker + Docs + DX
- ⏳ Week 6: Open Source Release

## Setup
```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your DATABASE_URL

# Start PostgreSQL (Docker)
docker start interceptr-db
```

## Running
```bash
# From ~/interceptr with venv active
uvicorn main:app --reload --port 8000
```

## Testing
```bash
pytest                          # run all tests
pytest tests/test_foo.py        # run a single test file
pytest -k "test_name"           # run a specific test by name
```

## Architecture
- `main.py` — FastAPI app instantiation, startup event (creates DB tables), and `/health` route
- `app/core/config.py` — Pydantic `Settings` class loading env vars from `.env`
- `app/core/database.py` — SQLAlchemy engine, `SessionLocal`, `Base` (DeclarativeBase), and `get_db()` dependency
- `app/models/` — SQLAlchemy model classes (extend `Base` from `app.core.database`)
- `app/schemas/` — Pydantic schemas for request/response validation
- `app/api/` — FastAPI routers; register them in `main.py` with `app.include_router(...)`
- `app/services/` — Business logic layer, called by API routes

Database sessions are injected via FastAPI's dependency injection using `get_db()`. All models must inherit from `Base` and be imported before `Base.metadata.create_all()` runs on startup.

## Project structure
```
interceptr/
├── app/
│   ├── __init__.py
│   ├── api/
│   │   ├── __init__.py
│   │   └── audit_logs.py         # Routes: POST / GET /api/v1/audit-logs
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py             # Loads .env via pydantic-settings
│   │   └── database.py          # SQLAlchemy engine, session, Base
│   ├── models/
│   │   ├── __init__.py
│   │   └── audit_log.py         # AuditLog SQLAlchemy model
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── audit_log.py         # Pydantic schemas: Create, Response, ListResponse
│   └── services/
│       ├── __init__.py
│       └── audit_log_service.py # create_log, get_logs
├── tests/
│   ├── conftest.py              # pytest fixtures, SQLite in-memory DB override
│   └── test_audit_logs.py       # Tests for audit log endpoints
├── docs/
├── main.py                      # FastAPI app entry point
├── requirements.txt
├── .env                         # Local only, never committed
├── .env.example                 # Committed, no real credentials
├── .gitignore
└── CLAUDE.md                    # This file
```

## Environment variables
| Variable | Description |
|---|---|
| `DATABASE_URL` | PostgreSQL connection string (required) |
| `APP_ENV` | `development` or `production` (default: `development`) |
| `APP_PORT` | Server port (default: `8000`) |
| `LOG_LEVEL` | Logging level (default: `INFO`) |

## Environment
- PostgreSQL in Docker
  - Container name: interceptr-db
  - User: interceptr
  - Password: interceptr123
  - Database: interceptr
  - Port: 5432
- Python virtual environment: ~/interceptr/venv
- Server port: 8000

## Key commands
```bash
# Check DB tables
docker exec -it interceptr-db psql -U interceptr -d interceptr -c "\dt"

# Start DB if container is stopped
docker start interceptr-db
```

## API endpoints
```
POST /api/v1/audit-logs     — Create a new audit log entry
GET  /api/v1/audit-logs     — Retrieve paginated audit logs
GET  /health                — Health check
```

## Data model — AuditLog
| Field | Type | Description |
|---|---|---|
| `id` | String (UUID) | Primary key, auto-generated |
| `timestamp` | DateTime (UTC) | Auto-generated on creation |
| `agent` | String | Who is making the call |
| `tool` | String | Which tool is being called |
| `arguments` | JSON | Arguments passed to the tool |
| `status` | Enum | `ALLOWED` or `BLOCKED` |
| `reason` | String (nullable) | Why it was blocked, null if allowed |

## Key decisions
- Sync SQLAlchemy (not async) — simpler, sufficient for this use case
- UUID as primary key for all models
- Tests use SQLite in-memory — no Docker dependency in CI
- All Python imports are absolute (from app.models.audit_log import ...)
- Every file has a one-line top-level comment in English describing its purpose
- No cloud infrastructure — 100% self-hosted, $0 operating cost

## Stack
- Python 3.12
- FastAPI 0.115.0
- Uvicorn 0.30.6
- SQLAlchemy 2.0.36 (sync)
- Alembic 1.13.3
- PostgreSQL 16 (Docker)
- Pydantic 2.9.2
- pydantic-settings 2.6.0
- python-dotenv 1.0.1
- pytest 8.3.3
- httpx 0.27.2

## Hardware
- Mac Mini M2 Pro 32GB — primary development machine
- MacBook Pro M3 Pro 18GB — secondary / mobile
- ASUS Zenbook Ubuntu 24.04 16GB — Docker/Linux testing

## AI tools in use
- Claude Code — primary coding agent
- Cursor Pro — editor with AI
- ChatGPT Pro / Codex — secondary reference
- Gemini Pro — secondary reference

## Links
- Landing: https://kelink.dev
- GitHub org: https://github.com/trykelink
- Repo: https://github.com/trykelink/interceptr

## Completed files

### Week 1 — Audit Logging
- `app/models/audit_log.py` — SQLAlchemy model with `AuditLog` table and `LogStatus` enum
- `app/schemas/audit_log.py` — Pydantic schemas: `AuditLogCreate`, `AuditLogResponse`, `AuditLogListResponse`
- `app/schemas/__init__.py` — Package init for schemas module
- `app/services/audit_log_service.py` — `create_log` and `get_logs` business logic
- `app/api/audit_logs.py` — FastAPI router with POST and GET `/api/v1/audit-logs`
- `main.py` — Updated to include audit_logs router and import model for table creation
- `tests/conftest.py` — pytest fixtures with SQLite in-memory DB via `StaticPool`, async `client` fixture
- `tests/test_audit_logs.py` — 4 async tests covering create (ALLOWED/BLOCKED) and list endpoints
- `pytest.ini` — Sets `testpaths = tests` and `pythonpath = .` for correct imports