<!-- policy-reference.md — Complete reference for Interceptr policy configuration -->
# Policy Reference

## File format
Interceptr policy files are YAML documents with this structure:

```yaml
version: "1.0"
agent: "support-agent"
rules:
  allow:
    - get_customer
    - list_orders
  deny:
    - delete_customer
default: "deny"
```

Fields:
- `version` (required): policy schema version. Current value is `"1.0"`.
- `agent` (required): target agent name or `"*"` wildcard.
- `rules` (required): mapping that can include `allow` and `deny` lists.
- `default` (required): fallback decision, either `"allow"` or `"deny"`.

## version
- Required field.
- Current supported value: `"1.0"`.

## agent
Controls which agent the policy applies to.

Examples:
```yaml
agent: "support-agent"   # exact match
```

```yaml
agent: "*"               # applies to all agents
```

If the incoming `agent` does not match and policy is not `"*"`, Interceptr allows the call.

## rules.allow
- List of explicitly permitted tools.
- If a tool is in `allow` and not in `deny`, decision is `ALLOWED`.

Example:
```yaml
rules:
  allow: ["get_customer", "list_orders"]
  deny: []
```

## rules.deny
- List of explicitly blocked tools.
- Always takes precedence over `allow`.

Example:
```yaml
rules:
  allow: ["delete_customer"]
  deny: ["delete_customer"]
```

Result: `delete_customer` is blocked.

## default
Fallback for tools in neither list.
- `"allow"`: unknown tools are allowed.
- `"deny"`: unknown tools are blocked (`reason: not_in_allowlist`).

## Evaluation order
Interceptr evaluates each tool call in this order:

```text
Incoming tool call
      |
      v
[deny list?] -- yes --> BLOCKED (policy_violation)
      |
      no
      v
[allow list?] -- yes --> ALLOWED
      |
      no
      v
[default]
  allow -> ALLOWED
  deny  -> BLOCKED (not_in_allowlist)
```

## Examples
### Minimal policy
```yaml
version: "1.0"
agent: "*"
rules:
  allow: []
  deny: []
default: "allow"
```

### Strict allowlist
```yaml
version: "1.0"
agent: "support-agent"
rules:
  allow:
    - get_customer
    - list_orders
  deny:
    - delete_customer
default: "deny"
```

### Monitoring-only (all allow)
```yaml
version: "1.0"
agent: "*"
rules:
  allow: []
  deny: []
default: "allow"
```

### Multi-agent setup using `*`
```yaml
version: "1.0"
agent: "*"
rules:
  allow:
    - get_customer
  deny:
    - delete_customer
    - execute_shell
default: "deny"
```

## Hot reload
Reload policy without restarting the API:

```bash
curl -X POST http://localhost:8000/api/v1/policy/reload
```

Notes:
- Reload returns `404` if no policy engine is configured.
- At startup, Interceptr auto-loads `policy.yaml` if the file exists.

## Best practices
- Start with `default: "deny"`.
- Explicitly define `allow` and `deny` lists.
- Keep `policy.yaml` under version control in your private repo (do not commit it to public repos if sensitive).
- Use `policy.example.yaml` as the committed template.
