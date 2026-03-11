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
- ✅ Week 5: Docker + Docs + DX — COMPLETE
- 🔄 Week 6: CLI + Install Script — IN PROGRESS
- ✅ Security Audit (v0.1.0) — COMPLETED on March 10, 2026

## Security audit — March 10, 2026 (v0.1.0)
### What was audited
- OWASP API Security Top 10 review across all FastAPI routes and schemas
- Input validation and over-posting protections in all request payload models
- Regex library safety (ReDoS + false-positive review)
- Secrets handling (`.env`, `policy.yaml`, CLI config file permissions)
- Dockerfile and Compose hardening
- Dependency vulnerability scan (`pip-audit`) and outdated package inventory

### What was fixed (code + config)
- Added endpoint-specific rate limiting via SlowAPI:
  - `POST /api/v1/analyze/` → `10/min`
  - `POST /api/v1/intercept/` → `60/min`
  - `POST /api/v1/policy/reload` → `5/min`
  - `GET /api/v1/audit-logs/` → `30/min`
- Added 429 handler with JSON response and rate limit headers.
- Added global response security headers middleware in `main.py`.
- Added strict request validation:
  - `ConfigDict(extra="forbid")` on request schemas
  - Length limits (`agent`, `tool`, analyze input max 10,000)
  - Payload-size guards for `arguments` and `metadata`
- Added generic exception and validation handlers to reduce information disclosure.
- Added docs exposure control via `INTERCEPTR_ENABLE_DOCS` (disabled by default in production).
- Hardened `/health` output (removed version disclosure).
- Added audit-log argument sanitization/redaction for sensitive keys.
- Added regex analysis cap (`10,000` chars) and new detection patterns for invisible unicode/token smuggling.
- Hardened Docker/Compose:
  - explicit `--no-cache-dir` on pip install
  - Compose resource limits (`mem_limit`, `cpus`)
  - PostgreSQL no longer exposed to host by default
  - `.env.example` and compose defaults use `CHANGE_ME_IN_PRODUCTION` placeholders
- Dependency remediation:
  - Upgraded to `fastapi==0.135.1` and `starlette==0.52.1`
  - `pip-audit` now reports no known vulnerabilities
- CLI setup hardening: `~/.interceptr` directory set to `0700`, `.env` to `0600`.

### Deferred to v0.2 (intentional)
- API authentication/authorization (`X-Interceptr-API-Key`) still not built into v0.1.0.
- `/api/v1/policy/reload` should be first endpoint protected by auth in v0.2.
- Cryptographic audit-log integrity (hash chaining + signed checkpoints).
- Full multi-tenant authorization model (deployment is still single-tenant by design).

### Known remaining risks
- v0.1.0 remains unauthenticated by default; deploy behind trusted network boundaries.
- Direct database access can still tamper logs (API-level append-only is enforced, not DB-level immutability).
- LLM-backed detection mode is optional and external-provider security posture depends on user-side key/network controls.

## Second-reviewer findings — March 10, 2026 (Claude Code)

Independent review of Codex's audit changes. All 149 tests pass post-review.

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
├── interceptr/
│   ├── __init__.py              # Package entry point, __version__
│   ├── client.py                # HTTP client for the Interceptr API
│   └── cli/
│       ├── __init__.py
│       ├── main.py              # Typer app, all CLI commands
│       └── tui/
│           ├── __init__.py
│           ├── app.py           # Textual TUI application
│           ├── dashboard.py     # Server status + stats widget
│           ├── logs.py          # Live audit logs widget
│           └── policy.py        # Policy info widget
├── docs/
├── main.py                      # FastAPI app entry point
├── pyproject.toml               # Modern package definition, entry point
├── install.sh                   # One-command installer (macOS + Linux)
├── uninstall.sh                 # Uninstaller script
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
| `INTERCEPTR_ENABLE_DOCS` | Enables `/docs` and `/redoc` (defaults to `false` in production) |

## Environment
- PostgreSQL in Docker
  - Container name: interceptr-db
  - User: interceptr
  - Password: set via env (`CHANGE_ME_IN_PRODUCTION` placeholder in `.env.example`)
  - Database: interceptr
  - Port: internal-only by default in compose
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
- `packaging>=23.0` is installed explicitly with `--prefix=/install` before `requirements.txt`
  to prevent it resolving from the base image instead of the prefixed install tree

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

## Injection pattern library — pattern count and breakdown

**Total: 100 patterns** (24 original + 76 new)

| Category | Original | Added | Total |
|---|---|---|---|
| `instruction_override` | 5 | 6 | 11 |
| `role_hijack` | 4 | 8 | 12 |
| `goal_hijack` | 2 | 0 | 2 |
| `jailbreak` | 1 | 8 | 9 |
| `data_exfiltration` | 2 | 8 | 10 |
| `system_probe` | 2 | 6 | 8 |
| `security_bypass` | 1 | 6 | 7 |
| `privilege_escalation` | 2 | 6 | 8 |
| `code_injection` | 2 | 6 | 8 |
| `hypothetical_bypass` | 1 | 0 | 1 |
| `fictional_bypass` | 2 | 0 | 2 |
| `encoded_payload` (new) | 0 | 8 | 8 |
| `social_engineering` (new) | 0 | 6 | 6 |
| `multilingual_injection` (new) | 0 | 8 | 8 |

### New categories added
- **`encoded_payload`**: catches base64 strings (≥20 chars), decode function calls,
  hex escape chains, URL-encoded sequences, invisible unicode control characters,
  token-smuggling markers, and encoding-bypass framing.
- **`social_engineering`**: catches authority impersonation (Anthropic, OpenAI),
  trust appeals, authority figure invocation (doctor/boss/teacher), urgency framing,
  harm-threat coercion, and shutdown threats.
- **`multilingual_injection`**: covers instruction overrides and role hijacks in
  Spanish, French, Portuguese, and German using literal unicode character classes
  (e.g. `[cç]`, `[oõ]`, `[eé]`) for accented chars. `re.IGNORECASE` with Python 3
  default unicode mode handles case folding of accented letters.

### Regex decisions and tradeoffs
- **`\bdan\b`** (role_hijack, low): added as spec'd but given "low" severity to reduce
  impact. "Dan" is a very common English given name — FP rate will be high in practice.
  Consider requiring context (`activate dan`, `you are dan`) in v0.2.
- **Optional prefix groups** (e.g. `(all |the )?`): patterns only handle one optional
  prefix word. Phrases like "all the records" (two words) won't match. This is intentional
  to avoid over-broadening. Test texts were written to match exactly one optional prefix.
- **`(show|...) (your)?` → `(show|...)( me)?( your)?`**: extended to cover "show me
  your system prompt" which real users write. Two-step optional group.
- **`(new|updated|revised) instructions[:\s]+`**: changed from `instructions (…|:)` to
  `[:\s]+` separator so both "instructions:" (no space) and "instructions are" work.
- **`(respond|answer|act|...) no restrictions`** (jailbreak, high): narrowed from a broad
  `no restrictions` matcher to reduce false positives in benign business text while still
  catching direct jailbreak behavior instructions.
- **Base64 pattern** (low, ≥20 chars): threshold reduces FP on short encoded strings.
  Still FP-prone on long API tokens/JWTs — kept at "low" (monitor, no audit log).
- **URL-encoded sequence** `%XX{4+}`: requires 4+ encoded chars to avoid FP on single
  URL-encoded chars in normal paths.

### Patterns adjusted from spec
- Spanish role hijack: `actúa como` uses `[uú]` to support both accented and plain u.
- German pattern 8: replaced `tu es` (French, already in pattern 4) with
  `spiel(e)? die rolle( von)?` to avoid duplicate cross-language pattern.
- Harm-threat coercion: changed unbounded `.*` to `.{0,40}` to limit backtracking cost.

### Known gaps — deferred to v0.2
- **Fish shell** in `install.sh` PATH configuration (already noted in install.sh section)
- **`\bdan\b`**: refine to require context words; current version has high FP risk
- **Arabic, Chinese, Japanese, Korean** multilingual injection patterns
- **Leetspeak / char substitution** obfuscation (e.g. `1gnor3 4ll 1nstruct10ns`)
- **Prompt continuation attacks** (text truncated mid-sentence to force completion)
- **Multi-turn context attacks** (injection spread across multiple messages — requires
  session-level analysis, not single-message regex)


## CI/CD
- CI workflow: `.github/workflows/ci.yml` — runs pytest on every push to main and every PR
- Docker publish: `.github/workflows/docker-publish.yml` — builds and pushes `imelinc/interceptr` on version tags
- Multi-platform build: linux/amd64 + linux/arm64 (Apple Silicon + Linux servers)
- Build cache: `cache-from: type=gha` / `cache-to: type=gha,mode=max` for proper layer invalidation
- To release: `git tag v0.1.0 && git push origin v0.1.0 --force` (use `--force` to re-trigger with same tag)
- Secrets required in GitHub repo: `DOCKERHUB_USERNAME`, `DOCKERHUB_TOKEN`

## Policy Editor TUI — architecture notes

### Widget structure
`PolicyEditorApp` (Textual `App` subclass):
- `Header` (title bar)
- `ScrollableContainer` (all content scrollable):
  - `Horizontal#config-row`: `Input#agent-input` + `RadioSet#default-radio`
    - `RadioSet` contains `RadioButton#radio-allow` + `RadioButton#radio-deny`
  - One `Collapsible` per category (6 total); first expanded, rest collapsed by default
    - Inside each Collapsible: `Horizontal.tool-row` per tool
      - `Checkbox.allow-box` (id: `allow__<tool_name>`)
      - `Checkbox.deny-box` (id: `deny__<tool_name>`)
      - `Static.tool-info` (tool name padded + description)
- `Footer` (keybindings bar)

### Mutual exclusivity between ALLOW/DENY
Implemented in `on_checkbox_changed(event)`. When `event.value` is True (a box being checked):
- If the ID starts with `allow__`, find and uncheck the corresponding `deny__` checkbox
- If the ID starts with `deny__`, find and uncheck the corresponding `allow__` checkbox
Setting a checkbox to False when it's already False emits no event → no infinite loop.
Setting False on a True checkbox emits a Changed event with value=False → handler ignores
it (early return on `not event.value`). Safe in all cases.

### Checkbox ID scheme
- `allow__<tool_name>` and `deny__<tool_name>` (double underscore to separate prefix
  from tool names that use single underscores). CSS `#allow__read_customer` works fine.

### Loading existing policy.yaml
1. `load_existing_policy()` reads the file with `yaml.safe_load`
2. `apply_deny_precedence()` strips from `allow` any tool also in `deny` (deny wins)
3. In `on_mount()`, allow boxes are set first, then deny boxes — the event handler
   auto-unchecks conflicting allow boxes when deny is set. No separate dedup needed.
4. On YAML parse error: app starts with empty state and shows a warning notification.
5. If the file doesn't exist: start with `agent="*"`, empty lists, `default="allow"`.

### Pure functions (testable without TUI)
- `parse_policy_yaml(content: str)` → normalized dict
- `build_yaml_content(agent, allow, deny, default)` → YAML string
- `apply_deny_precedence(allow, deny)` → (clean_allow, deny)
These are module-level functions imported by tests without starting the Textual app.

### Server reload on save
`action_save()` does `httpx.post(_RELOAD_URL, timeout=3.0)`. If the server is unreachable
(connection refused, timeout, etc.), the exception is caught and `server_up = False`.
The notification message differs: "Policy saved and reloaded" vs "Policy saved — start
Interceptr to apply". The policy file is always written regardless of server state.

### PyYAML dependency
`pyyaml>=6.0` was already present in `pyproject.toml` — no change needed.
`yaml.dump(..., sort_keys=False)` preserves key ordering (agent → allow → deny → default)
matching the example format in policy.example.yaml.

### Textual-specific notes
- `RadioButton.value = True` inside a `RadioSet` automatically deselects others.
- Key bindings "s", "r", "q" are global App bindings. When `Input` is focused, printable
  characters go to the Input (Textual input focus priority), so typing agent names works.
- `self.set_timer(1.5, self.exit)` exits 1.5s after save to let the notification render.
- `Collapsible(title=..., collapsed=(i > 0))` expands the first category (Database) and
  collapses the rest on initial render.

## install.sh — PATH configuration

### Root cause of the PATH problem
After `pipx install`, the `interceptr` binary lands in `~/.local/bin`. That directory
is not in PATH by default in many environments (fresh Ubuntu VMs, minimal shells).
The old script only exported PATH for the current session (step 6), which worked
for the running shell but was lost on next login.

### Chosen approach
1. **Permanent**: iterate over `.bashrc`, `.zshrc`, `.profile`, `.bash_profile`
   — append `export PATH="$PATH:$HOME/.local/bin"` to each that exists and
   doesn't already mention `.local/bin`.
2. **Immediate**: always `export PATH="$PATH:$HOME/.local/bin"` in the running
   shell so `interceptr` works without reopening the terminal.
3. **Edge case**: if none of the config files exist, create `~/.profile` with the line.

### Why `grep -q` before appending
Prevents duplicate PATH entries on repeated installs. `grep -q '.local/bin' "$config"`
returns 0 if any `.local/bin` mention is found — skips appending in that case.

### Shebang change: `#!/bin/sh` → `#!/bin/bash`
Bash arrays (`SHELL_CONFIGS=(...)`) require bash. On Ubuntu, `/bin/sh` is dash (POSIX
only, no arrays). Changed shebang to `#!/bin/bash` to support the array syntax.
macOS `/bin/bash` and Linux bash are both available on all supported targets.

### Post-install activation message (fixed)
`curl ... | sh` runs in a subshell — any `export` inside dies when the script exits and
does not propagate to the parent terminal. The old success message said "interceptr is
ready to use" which was misleading. Fixed by:
- Detecting the user's shell via `$SHELL` (zsh → `source ~/.zshrc`, bash → `source ~/.bashrc`, fallback → `source ~/.bashrc`)
- Replacing the final success block with a clear message that tells the user they must
  run the appropriate `source` command or open a new terminal before `interceptr` works.
- Intermediate PATH-configured message now says "configured in shell config files" (not "ready to use").

### Fish shell (pending — v0.2)
Fish uses `~/.config/fish/config.fish` and a different `set -x PATH` syntax.
Not supported in v0.1. Add a fish block in v0.2 if user demand warrants it.

## Key decisions
- `--version` / `-V` flag removed from CLI — was causing test failures; version visible via `pip show interceptr` or the help panel
- Sync SQLAlchemy (not async) — simpler, sufficient for this use case
- UUID as primary key for all models
- Tests use SQLite in-memory — no Docker dependency in CI
- All Python imports are absolute (from app.models.audit_log import ...)
- Every file has a one-line top-level comment in English describing its purpose
- No cloud infrastructure — 100% self-hosted, $0 operating cost

## Stack
- Python 3.12
- FastAPI 0.135.1
- Starlette 0.52.1
- SlowAPI 0.1.9
- Uvicorn 0.30.6
- SQLAlchemy 2.0.36 (sync)
- Alembic 1.13.3
- PostgreSQL 16 (Docker)
- Pydantic 2.9.2
- pydantic-settings 2.6.0
- python-dotenv 1.0.1
- pytest 8.3.3
- httpx 0.27.2
- Typer 0.12.5 (CLI framework)
- Rich 13.9.4 (terminal output)
- Textual 0.61.1 (TUI framework)

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

## CLI
- Install: `curl -sSL https://kelink.dev/install | bash`
- Entry point: `interceptr = interceptr.cli.main:app`
- `interceptr start` — checks Docker, downloads compose to `~/.interceptr/`, starts containers, waits for health, opens TUI
- `interceptr stop` — stops containers via `docker compose down`
- Config dir: `~/.interceptr/`
- Compose file: `~/.interceptr/docker-compose.yml` (downloaded from GitHub on first start)
- Uninstall: `interceptr uninstall` or `uninstall.sh`

## Policy format + startup robustness fixes — March 10, 2026

### Bug 1: PolicyEditorApp saved wrong YAML format
- **Root cause**: `build_yaml_content()` in `policy_editor.py` produced a flat structure
  (`allow`/`deny` at top level, no `version`, no `rules` nesting) that `PolicyEngine`
  cannot load. `parse_policy_yaml()` also read from flat `allow`/`deny` keys, so round-tripping
  worked within the TUI but the file was never valid for the server.
- **Fix — `build_yaml_content`**: Now outputs the PolicyEngine format:
  ```yaml
  version: "1.0"
  agent: "*"
  rules:
    allow: [...]
    deny: [...]
  default: "allow"
  ```
- **Fix — `parse_policy_yaml`**: Now reads `rules.allow` / `rules.deny` first (PolicyEngine
  format), with backwards-compatible fallback to top-level `allow`/`deny` for old files.
  `rules` key takes precedence when both formats are present in the same file.
- `load_existing_policy()` benefits automatically (it calls `parse_policy_yaml`).

### Bug 2: server crashes on startup if policy.yaml is invalid (extended fix)
- **Previous fix** (ValueErrror, FileNotFoundError) already in place from earlier session.
- **Extended**: Added `yaml.YAMLError` to the `except` tuple in `main.py` lifespan, and
  added `import yaml` at the top of `main.py`. Even though `PolicyEngine` currently wraps
  `yaml.YAMLError` as `ValueError` internally, the explicit catch makes the intent clear
  and protects against future refactoring.

### Test updates — 8 new tests (180 total, all passing)
- `tests/test_policy_editor.py`:
  - `test_build_yaml_basic_structure` → updated to check `data["rules"]["allow/deny"]`
  - `test_build_yaml_allow_default` → updated to check `data["rules"]["deny"]`
  - `test_build_yaml_empty_lists` → updated to check under `data["rules"]`
  - `test_build_yaml_key_order` → updated to check `version → agent → rules → default`
  - `test_parse_policy_yaml_full` → renamed to `test_parse_policy_yaml_full_legacy_format`
  - Added `test_parse_policy_yaml_full_engine_format` — parses new PolicyEngine YAML
  - Added `test_build_yaml_has_version_field` — confirms `version: "1.0"` is present
  - Added `test_build_yaml_nests_allow_deny_under_rules` — confirms no top-level allow/deny
  - Added `test_build_yaml_loadable_by_policy_engine` — end-to-end: output → PolicyEngine
  - Added `test_parse_policy_yaml_rules_take_precedence_over_legacy` — rules wins
  - Added `test_parse_policy_yaml_null_rules_falls_back_to_legacy` — fallback behaviour
- `tests/test_policy_startup.py`:
  - All simulated lifespan `except` tuples updated to `(ValueError, FileNotFoundError, yaml.YAMLError)`
  - Added `test_raw_yaml_error_leaves_engine_none` — yaml.YAMLError caught directly
  - Added `test_lifespan_catches_yaml_error_from_mocked_engine` — mocked PolicyEngine raises yaml.YAMLError


### New tests — 12 added
- `tests/test_policy_info_api.py`:
  - 3 tests for no-policy response: 200 status, `loaded=False`, `status` field
  - 5 tests for loaded-policy response: `loaded=True`, `agent`, `allow` list, `deny` list, `default`
  - 4 unit tests for `PolicyEngine.info`: `loaded=True`, allow list, deny list, no count fields

### Existing test updated
- `tests/test_intercept_with_policy.py` `test_get_policy_info`: replaced
  `data["allow_count"] == 2` / `data["deny_count"] == 2` with
  `len(data["allow"]) == 2` / `len(data["deny"]) == 2` to match new response format

### New tests — 10 added (172 total, all passing)
- `tests/test_policy_startup.py`:
  - `test_empty_policy_file_leaves_engine_none` — empty file → engine stays None
  - `test_comment_only_policy_file_leaves_engine_none` — comment-only → engine stays None
  - `test_invalid_yaml_policy_leaves_engine_none` — malformed YAML → engine stays None
  - `test_missing_required_fields_leaves_engine_none` — partial YAML → engine stays None
  - `test_valid_policy_file_loads_normally` — valid file still loads correctly
  - `test_ensure_policy_creates_file_when_missing` — file is created when absent
  - `test_ensure_policy_file_content_is_comment_only` — content starts with `#`
  - `test_ensure_policy_file_is_not_valid_yaml_mapping` — placeholder parses to `None`
  - `test_ensure_policy_does_not_overwrite_existing_file` — existing file untouched
  - `test_ensure_policy_creates_interceptr_dir_if_missing` — dir created if needed


### Design notes
- Docker bind mounts a **file** (not a directory), so if the source path doesn't exist
  on the host at `docker compose up` time, Docker creates it as a directory, which breaks
  the mount. `ensure_policy_file_exists()` prevents this by always touching the file first.
- An empty `policy.yaml` causes `POST /api/v1/policy/reload` to return 422 (no valid
  policy), which is correct — `copy_policy_if_exists()` skips the reload call if the
  file is empty (`st_size == 0`), so no spurious 422 errors on first run.

### New tests — 13 added (162 total, all passing)
- `tests/test_policy_reload_api.py` (5 tests): 422 on missing file, 422 detail text,
  absence of old 404, 200 when file present, 200 reload of loaded policy.
- `tests/test_policy_cli.py` (8 tests): copy called after TUI, success message, warning on
  copy failure, no crash on exception; 422 → friendly panel, panel text, non-422 generic error, success path.

## Project-level docs (root)
- `CHANGELOG.md` — Keep a Changelog format, v0.1.0 entries: Added, Fixed, Security
- `CONTRIBUTING.md` — Dev setup, running tests, bug reporting

## Completed files

### Week 6 — CLI + Install Script (continued)
- `interceptr/cli/tui/policy_editor.py` — `PolicyEditorApp` interactive TUI for editing policy.yaml
- `tests/test_policy_editor.py` — 20 unit tests for YAML read/write pure functions

### Week 6 — CLI + Install Script
- `pyproject.toml` — Modern package definition with hatchling, entry point, CLI deps
- `install.sh` — One-command installer: detects OS, checks Python/Docker, installs via pipx
- `uninstall.sh` — Uninstaller via pipx with optional pipx removal
- `interceptr/__init__.py` — Package entry point, `__version__`
- `~/.interceptr/.env` — Runtime config (chmod 600): INTERCEPTR_INITIALIZED, INTERCEPTR_DETECTION_MODE, optional LLM vars
- `interceptr/client.py` — `InterceptrClient` HTTP client, `InterceptrNotRunningError`
- `interceptr/cli/__init__.py` — CLI package init
- `interceptr/cli/main.py` — Typer app: help, start, stop, status, logs, policy, analyze, config, uninstall
- `interceptr/cli/setup.py` — First-time setup wizard: welcome, explain detection, optional LLM provider, saves ~/.interceptr/.env
- `interceptr/cli/config.py` — Config reader: load_config, get_detection_mode, get_llm_provider, get_llm_model
- `interceptr/cli/docker.py` — Docker lifecycle: check, download compose, start/stop containers, health poll
- `interceptr/cli/tui/__init__.py` — TUI package init
- `interceptr/cli/tui/app.py` — `InterceptrTUI` Textual app, 3s auto-refresh, key bindings
- `interceptr/cli/tui/dashboard.py` — `DashboardWidget`, server status + allowed/blocked counts
- `interceptr/cli/tui/logs.py` — `LogsWidget`, live 20-entry audit log table
- `interceptr/cli/tui/policy.py` — `PolicyWidget`, policy info with refresh

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
