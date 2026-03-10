<!-- SECURITY.md — Security posture, controls, and disclosure policy for Interceptr. -->
# Security

## Security Model
Interceptr is a FastAPI-based security middleware that inspects agent tool calls before execution.
The primary threat model is malicious or manipulated agent inputs (prompt injection, policy bypass attempts)
and abusive API usage against the middleware itself.

Current protection layers include:
- Policy-based allow/deny enforcement for intercepted tools
- Prompt injection analysis with curated regex detection
- Immutable-style API behavior for audit logs (append/read only)
- Per-endpoint rate limiting to reduce abuse and resource exhaustion
- Security headers and hardened error responses
- Secrets hygiene controls (`.env` and `policy.yaml` gitignored, CLI config file permissions)
- API docs exposure control via `INTERCEPTR_ENABLE_DOCS` (production-safe default)

## Known Risks & Mitigations
- No built-in API authentication in v0.1.0
  - Risk: Any network-reachable client can call interception, analysis, policy reload, and audit endpoints.
  - Mitigation: Deploy behind a private network, reverse proxy, firewall, or service mesh auth layer.
- Policy reload endpoint is high-value and currently unauthenticated
  - Risk: Unauthorized policy reload attempts if endpoint is exposed.
  - Mitigation: Restrict network access to trusted operators only; prioritize API key auth in v0.2.
- No tenant isolation model yet
  - Risk: Multi-tenant deployments could mix audit visibility if not isolated externally.
  - Mitigation: Use one deployment per tenant/workspace in v0.1.0.
- Secrets exposure via misconfigured environments
  - Risk: Weak file permissions or accidental commit of runtime secrets.
  - Mitigation: `~/.interceptr/.env` is written with `0600`, parent directory with `0700`, and `.env`/`policy.yaml` are ignored by git.
- Audit trail integrity is not cryptographically sealed
  - Risk: Direct DB administrators can still alter rows outside API paths.
  - Mitigation: Restrict DB access and use external backups; add hash chaining in v0.2.
- CORS behavior
  - Risk: Misconfigured permissive CORS can expose admin flows to browser-based abuse.
  - Mitigation: No wildcard CORS middleware is enabled by default.

## Rate Limiting
SlowAPI rate limiting is enabled with per-IP limits:
- `POST /api/v1/analyze/`: `10/minute`
- `POST /api/v1/intercept/`: `60/minute`
- `POST /api/v1/policy/reload`: `5/minute`
- `GET /api/v1/audit-logs/`: `30/minute`

Behavior:
- Exceeded requests return HTTP `429` with JSON `{"detail":"Too many requests"}`
- Responses include `X-RateLimit-Limit` and `X-RateLimit-Remaining` headers

## Security Headers
All API responses include:
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `X-XSS-Protection: 1; mode=block`
- `Strict-Transport-Security: max-age=31536000; includeSubDomains`
- `Referrer-Policy: strict-origin-when-cross-origin`
- `Content-Security-Policy: default-src 'none'`
- `Cache-Control: no-store`
- `Permissions-Policy: geolocation=(), microphone=(), camera=()`

## Authentication (v0.2 Roadmap)
Planned for v0.2:
- API key authentication for all endpoints using `X-Interceptr-API-Key`
- Key generation via `interceptr config`
- Key storage in `~/.interceptr/.env`
- Policy reload endpoint (`/api/v1/policy/reload`) is first auth priority due impact

## Reporting a Vulnerability
- Email: `security@kelink.dev`
- Response-time commitment: first response within `48 hours`
- Please do not publicly disclose vulnerabilities before a fix is available

Include in reports:
- Affected version/tag
- Reproduction steps
- Expected vs actual behavior
- Logs, request samples, or PoC details (if available)

## Dependency Audit
Audit run date: March 10, 2026.

Commands executed:
- `pip-audit`
- `pip list --outdated`

Results:
- Initial scan found known vulnerabilities in `starlette==0.38.6` (`CVE-2024-47874`, `CVE-2025-54121`)
- Remediated by upgrading to `fastapi==0.135.1` and `starlette==0.52.1`
- Post-remediation `pip-audit` result: no known vulnerabilities found

Notes:
- Several packages are outdated but not flagged as vulnerable in the current scan
- Dependency updates should continue in regular maintenance cycles

## Docker Security
Current hardening includes:
- Runtime container runs as non-root user `interceptr`
- Multi-stage build with reduced runtime footprint
- No `.env` copied into image
- `pip install` uses `--no-cache-dir`
- Healthcheck configured against `/health`
- Compose services use `restart: unless-stopped`
- Compose resource limits applied (`mem_limit` and `cpus`)
- PostgreSQL uses named volume `postgres_data`

PostgreSQL exposure:
- `docker-compose.yml` keeps PostgreSQL internal by default
- Expose `5432` only in development scenarios where host access is explicitly needed

## Audit Trail Integrity
Current state:
- Audit logs are append/read only at API level (no update/delete endpoints)
- Timestamps are server-side and UTC-based in the model
- Sensitive argument keys (for example `password`, `token`, `api_key`) are redacted in audit payloads

Future enhancement (recommended):
- Add cryptographic hash chaining for tamper-evident audit records
- Add periodic integrity verification job and signed checkpoint snapshots
