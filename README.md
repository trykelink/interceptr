# Interceptr

> AI agent security middleware by [Kelink](https://kelink.dev)

Interceptr is a proxy that sits between your AI agent and the outside world. Every tool call the agent attempts passes through Interceptr before it executes. The core principle: **nothing runs without inspection**.

---

## Why Interceptr

AI agents are being deployed in production with real access to databases, APIs, and file systems. Most teams ship them without visibility into what the agent is actually doing, without a way to control what actions it can take, and without a record of what happened when something went wrong.

Interceptr solves that.

---

## Features (MVP)

- **Audit Logging** — Every action is logged with timestamp, agent, tool, arguments, status, and reason
- **Tool Call Interceptor** — Intercepts every tool call before execution and decides allow or deny *(coming Week 2)*
- **Policy Engine** — Define what your agent can and cannot do via a simple YAML file *(coming Week 3)*
- **Prompt Injection Detection** — Detects and blocks malicious inputs before they reach the agent *(coming Week 4)*

---

## Quickstart

### Requirements
- Python 3.12+
- Docker

### 1. Clone the repo

```bash
git clone https://github.com/trykelink/interceptr.git
cd interceptr
```

### 2. Create the virtual environment

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Configure environment

```bash
cp .env.example .env
```

Edit `.env` with your database credentials.

### 4. Start PostgreSQL

```bash
docker run -d \
  --name interceptr-db \
  -e POSTGRES_USER=interceptr \
  -e POSTGRES_PASSWORD=interceptr123 \
  -e POSTGRES_DB=interceptr \
  -p 5432:5432 \
  postgres:16
```

### 5. Run the server

```bash
uvicorn main:app --reload --port 8000
```

Server is live at `http://localhost:8000`

---

## API

### Health check
```
GET /health
```

### Audit Logs
```
POST /api/v1/audit-logs/    — Create a log entry
GET  /api/v1/audit-logs/    — Retrieve paginated logs
```

**Example — log a blocked tool call:**
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

---

## Running tests

```bash
pytest tests/ -v
```

---

## Project structure

```
interceptr/
├── app/
│   ├── api/          # FastAPI routers
│   ├── core/         # Config and database setup
│   ├── models/       # SQLAlchemy models
│   ├── schemas/      # Pydantic schemas
│   └── services/     # Business logic
├── tests/
├── main.py
└── requirements.txt
```

---

## Roadmap

- [x] Audit Logging
- [ ] Tool Call Interceptor
- [ ] Policy Engine (YAML)
- [ ] Prompt Injection Detection
- [ ] Docker one-liner
- [ ] Open source release v0.1.0

---

## License

MIT — free to use, self-host, and modify.

---

Built by [Kelink](https://kelink.dev)