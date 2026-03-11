# Changelog

All notable changes to Interceptr are documented here.
Format: [Keep a Changelog](https://keepachangelog.com/en/1.0.0/)
Versioning: [Semantic Versioning](https://semver.org/)

## [Unreleased]

## [0.1.0] - 2026-03-11

### Added
- AI agent tool call interception via `POST /api/v1/intercept/` — every tool call is evaluated before execution.
- Prompt injection detection with 100 regex patterns across 14 categories: instruction override, role hijack, goal hijack, jailbreak, data exfiltration, system probe, security bypass, privilege escalation, code injection, hypothetical/fictional bypass, encoded payloads, social engineering, and multilingual injection (ES, FR, PT, DE).
- YAML policy engine with allow/deny lists, wildcard agent support (`"*"`), configurable default action, and hot reload via `POST /api/v1/policy/reload`.
- Audit logging for every intercepted tool call, with TTL-based cleanup and automatic argument redaction for sensitive keys.
- `POST /api/v1/analyze/` endpoint for standalone prompt injection analysis — returns severity, matched patterns, and a block/monitor/allow recommendation.
- Interactive TUI dashboard (Textual) with real-time audit log table, server status, and policy panel; auto-refreshes every 3 seconds.
- Interactive policy editor TUI with per-tool allow/deny checkboxes, mutual-exclusivity enforcement, and live server reload on save.
- CLI with commands: `start`, `stop`, `status`, `logs`, `policy show/edit/reload`, `analyze`, `config`, and `uninstall`.
- First-time setup wizard (`interceptr start`) with optional LLM provider configuration for enhanced detection.
- One-command installer for macOS and Linux: `curl -sSL https://raw.githubusercontent.com/trykelink/interceptr/main/install.sh | bash`.
- Multi-stage Docker build (`python:3.12-slim` base, non-root runtime user, target image size under 200 MB).
- `docker-compose.yml` for running the full stack (Interceptr + PostgreSQL) with health-gated startup and resource limits.
- `policy.yaml` volume mount in Compose for policy persistence across container restarts.
- GitHub Actions CI/CD: test suite runs on every push and pull request; Docker Hub image published on version tags for `linux/amd64` and `linux/arm64`.
- `GET /api/v1/policy/` endpoint returning current policy state (agent, allow list, deny list, default action, loaded flag).
- `GET /api/v1/audit-logs/` endpoint with pagination support.
- `/health` endpoint for container and load-balancer health checks.

### Fixed
- Policy YAML format mismatch between the TUI editor and `PolicyEngine` — editor now writes the correct `version`/`rules` nesting that the server expects.
- Server no longer crashes on startup when `policy.yaml` is empty, comment-only, has invalid YAML syntax, or is missing required fields.
- Policy file is created on disk before Docker starts so volume mounts bind to a file rather than a directory.
- `packaging` module not found in the Docker image — now installed explicitly before `requirements.txt` to prevent resolution from the base image.
- Docker layer cache not invalidated correctly in GitHub Actions — Compose now uses the published image instead of a local build in CI.
- `interceptr` binary unavailable after install without reopening the terminal — installer now patches all active shell config files and prints a clear `source` instruction.

### Security
- Per-endpoint rate limiting via SlowAPI: `POST /api/v1/analyze/` (10/min), `POST /api/v1/intercept/` (60/min), `POST /api/v1/policy/reload` (5/min), `GET /api/v1/audit-logs/` (30/min).
- Security headers added to all responses: `X-Content-Type-Options`, `X-Frame-Options`, `X-XSS-Protection`, `Referrer-Policy`, `Content-Security-Policy`.
- Request payload hardened with `extra="forbid"` on all Pydantic schemas, field length limits, and payload size guards.
- Sensitive keys (tokens, passwords, secrets, API keys) automatically redacted in stored audit log arguments.
- Regex pattern library validated to be ReDoS-resistant; analysis input capped at 10,000 characters.
- Prompt injection detection runs before tool execution — high/medium findings automatically create an audit log entry.
- `~/.interceptr` config directory created with permissions `0700`; `.env` written with `0600`.
- `/docs` and `/redoc` disabled by default in production; opt-in via `INTERCEPTR_ENABLE_DOCS=true`.
- `/health` response hardened — no longer discloses application version.
- Generic exception and validation-error handlers prevent internal stack traces from leaking in API responses.
