<p align="center">
  <img src="/docs/banner-interceptr.png" alt="Interceptr banner">
</p>

<h1 align="center">Interceptr</h1>

<p align="center">
  AI Agent Security Middleware<br>
  <strong>Inspect. Control. Audit.</strong>
</p>

<p align="center">
  Built by <a href="https://kelink.dev">Kelink</a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/python-3.12-blue.svg" alt="Python 3.12">
  <img src="https://img.shields.io/badge/fastapi-0.115.0-green" alt="FastAPI 0.115.0">
  <img src="https://img.shields.io/badge/license-MIT-black" alt="MIT License">
  <img src="https://img.shields.io/badge/status-MVP-orange" alt="MVP status">
  <img src="https://img.shields.io/badge/AI%20Agents-Security-red" alt="AI agent security">
</p>

---

## What Interceptr Is

**Interceptr** is an open source security layer for AI agents.

It sits between an agent and the tools it wants to use, so every action can be inspected before it runs.

> **Nothing runs without inspection.**

Today, the project includes the first building block of that system: **audit logging for agent actions**. The broader interception, policy, and prompt-defense layers are on the roadmap below.

## Why It Exists

AI agents are starting to operate with access to real systems:

- APIs
- databases
- file systems
- email
- internal tools

That makes them useful, but it also makes them risky. Without a security layer, a compromised or manipulated agent can trigger:

- unauthorized tool execution
- data exfiltration
- privilege escalation
- prompt injection-driven behavior

Interceptr is designed to act like a firewall for agent actions.

## How It Works

```text
User
  |
AI Agent
  |
Interceptr
  |
Policy + Inspection Layer
  |
Tool Execution
```

The intended execution flow is:

1. An agent attempts a tool call.
2. Interceptr intercepts the action.
3. Security rules evaluate the request.
4. The action is allowed or blocked.
5. The decision is recorded in the audit trail.

## Current Status

`v0.1` is focused on **audit logging**.

Implemented today:

- FastAPI service for recording agent actions
- PostgreSQL-backed audit log storage
- structured fields for `agent`, `tool`, `arguments`, `status`, `reason`, and `timestamp`
- list endpoint for retrieving stored logs
- test coverage for create and list flows

Planned next:

- tool call interception
- YAML policy engine
- prompt injection detection

## Audit Logging

Every audited action stores:

- `agent`
- `tool`
- `arguments`
- `timestamp`
- `status`
- `reason`

Example payload:

```json
{
  "agent": "customer-support-agent",
  "tool": "delete_customer",
  "arguments": {
    "id": "123"
  },
  "status": "BLOCKED",
  "reason": "policy_violation"
}
```

## Quickstart

### Requirements

- Python 3.12+
- Docker

### 1. Clone the repository

```bash
git clone https://github.com/trykelink/interceptr.git
cd interceptr
```

### 2. Create a virtual environment and install dependencies

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Configure environment variables

```bash
cp .env.example .env
```

Then update `DATABASE_URL` in `.env`.

Example:

```env
DATABASE_URL=postgresql://interceptr:interceptr123@localhost:5432/interceptr
APP_ENV=development
APP_PORT=8000
LOG_LEVEL=INFO
```

### 4. Start PostgreSQL

If you are creating the container for the first time:

```bash
docker run -d \
  --name interceptr-db \
  -e POSTGRES_USER=interceptr \
  -e POSTGRES_PASSWORD=interceptr123 \
  -e POSTGRES_DB=interceptr \
  -p 5432:5432 \
  postgres:16
```

If the container already exists:

```bash
docker start interceptr-db
```

### 5. Run the API

```bash
uvicorn main:app --reload --port 8000
```

Once running:

- API: `http://localhost:8000`
- Docs: `http://localhost:8000/docs`
- Health check: `http://localhost:8000/health`

## API

### Endpoints

- `GET /health`
- `POST /api/v1/audit-logs/`
- `GET /api/v1/audit-logs/`

### Example: create a blocked audit log

```bash
curl -X POST http://localhost:8000/api/v1/audit-logs/ \
  -H "Content-Type: application/json" \
  -d '{
    "agent": "customer-support-agent",
    "tool": "delete_customer",
    "arguments": {"id": "123"},
    "status": "BLOCKED",
    "reason": "policy_violation"
  }'
```

## Running Tests

```bash
pytest tests/ -v
```

## Project Structure

```text
interceptr/
├── app/
│   ├── api/          # FastAPI routers
│   ├── core/         # Config and database setup
│   ├── models/       # SQLAlchemy models
│   ├── schemas/      # Pydantic schemas
│   └── services/     # Business logic
├── docs/             # Images and project assets
├── tests/            # API tests
├── main.py           # FastAPI entry point
└── requirements.txt
```

## Roadmap

- `v0.1` Audit logging
- `v0.2` Tool call interceptor
- `v0.3` YAML policy engine
- `v0.4` Prompt injection detection
- `v1.0` Production-ready release

## Contributing

Contributions are welcome. Open an issue or submit a pull request.

## License

MIT. Free to use, modify, and self-host.

<p align="center">
  Built by <a href="https://kelink.dev">Kelink</a>
</p>