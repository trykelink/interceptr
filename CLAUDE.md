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
- ✅ Week 2: Tool Call Interceptor — COMPLETE
- ✅ Week 3: Policy Engine with YAML — COMPLETE
- ✅ Week 4: Prompt Injection Detection — COMPLETE
- 🔄 Week 5: Docker + Docs + DX — IN PROGRESS
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

## Docker
```bash
# Build the production image
docker build -t interceptr:local .

# Start full stack (Interceptr + PostgreSQL) via Compose
docker compose up --build -d

# Stop and remove containers + volumes
docker compose down -v

# View logs
docker compose logs interceptr

# Check container health
docker compose ps
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

## Docker
```bash
# Build image
docker build -t interceptr .

# Run local stack (Interceptr + PostgreSQL)
docker compose up
```

- Runtime user: `interceptr` (non-root)
- Healthcheck: `GET /health`
- Build strategy: multi-stage Dockerfile
- Target final image size: under 200MB

## API endpoints
```
POST /api/v1/audit-logs     — Create a new audit log entry
GET  /api/v1/audit-logs     — Retrieve paginated audit logs
GET  /health                — Health check
POST /api/v1/intercept/     — Intercept a tool call and get an allow/deny decision
GET  /api/v1/policy/        — Get current policy info
POST /api/v1/policy/reload  — Reload policy from disk
POST /api/v1/analyze/       — Analyze input text for prompt injection patterns
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

## Policy Engine behavior
- deny list checked first (always blocks even if tool is also in allow)
- allow list checked second
- default applied if tool is in neither list
- agent wildcard `"*"` matches all agents
- agent mismatch → ALLOWED (policy doesn't apply)
- `policy.yaml` loaded on startup if present, otherwise all tool calls are ALLOWED
- `policy.yaml` must NOT be committed to git; `policy.example.yaml` is the reference

## Injection Detection behavior
- Pattern library in `injection_patterns.py` — pure data, no logic
- `InjectionDetector` compiles all patterns at startup
- Severity precedence: high > medium > low
- high/medium → recommendation=`"block"`, creates audit log automatically
- low → recommendation=`"monitor"`, no audit log
- clean → recommendation=`"allow"`, no audit log


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

### Week 5 — Docker + Docs + DX
- `Dockerfile` — Multi-stage production build (builder + final), non-root runtime, `/health` healthcheck
- `.dockerignore` — Docker build context exclusions for faster and cleaner builds
- `docker-compose.yml` — Local development stack for Interceptr + PostgreSQL with health-gated startup
- `.env.example` — Updated with Docker/Compose defaults for app and PostgreSQL
- `docs/quickstart.md` — 5-minute setup guide (Docker Compose + local dev), first interception, and verification
- `docs/policy-reference.md` — Complete YAML policy reference, evaluation order, examples, and hot reload
- `docs/openai-integration.md` — OpenAI Agents SDK integration with interception wrapper and pre-agent analyze flow
- `docs/index.md` — Documentation index linking quickstart, policy reference, and integration guide

### Week 4 — Prompt Injection Detection
- `app/core/injection_patterns.py` — Curated prompt injection regex library grouped by severity
- `app/core/injection_detector.py` — `InjectionDetector` and `AnalysisResult` with severity precedence and recommendations
- `app/schemas/analysis.py` — Pydantic schemas for analysis request/response payloads
- `app/api/analyze.py` — FastAPI router with POST `/api/v1/analyze/` and conditional blocked audit logging
- `main.py` — Updated to include analyze router
- `tests/test_injection_detector.py` — 14 unit tests for detection patterns, severity, and recommendations
- `tests/test_analyze_endpoint.py` — 8 integration tests for endpoint behavior and audit log creation rules

### Architecture decisions - Week 4
- Injection detection uses regex pattern matching (not LLM guard) — $0 cost, 
  offline, deterministic, <1ms per request. Covers ~80% of known attack vectors.

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

### Week 3 — Policy Engine with YAML
- `policy.example.yaml` — Reference policy file for users to copy and customize
- `app/core/policy_engine.py` — `PolicyEngine` class: loads YAML, evaluates tool calls against rules
- `app/schemas/policy.py` — Pydantic schemas: `PolicyInfo`, `PolicyReloadResponse`
- `app/api/policy.py` — FastAPI router with GET `/api/v1/policy/` and POST `/api/v1/policy/reload`
- `main.py` — Updated to load `PolicyEngine` on startup if `policy.yaml` exists
- `tests/test_policy_engine.py` — 10 unit tests for PolicyEngine class
- `tests/test_intercept_with_policy.py` — 6 integration tests for interception with policy active

### Week 2 — Tool Call Interceptor
- `app/schemas/intercept.py` — Pydantic schemas: `InterceptRequest`, `InterceptDecision`, `InterceptResponse`
- `app/services/interceptor_service.py` — `InterceptorService` class with `evaluate()` and `intercept()` methods; module-level `interceptor_service` singleton
- `app/api/intercept.py` — FastAPI router with POST `/api/v1/intercept/`
- `main.py` — Updated to include intercept router
- `tests/test_intercept.py` — 5 async tests covering allowed decision, audit log auto-creation, log_id UUID validation, metadata, and missing fields

## Architecture decisions — Week 2
- `InterceptorService` uses dependency injection for `policy_engine` (None in Week 2, injected in Week 3)
- `intercept()` always creates an audit log regardless of decision (ALLOWED or BLOCKED)
- Module-level singleton `interceptor_service` instantiated in `interceptor_service.py`
