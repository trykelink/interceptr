# policy_engine.py — Reads YAML policy files and evaluates tool calls against defined rules
import yaml
from app.schemas.intercept import InterceptDecision, InterceptRequest


class PolicyEngine:
    def __init__(self, policy_path: str):
        self.policy_path = policy_path
        self._load_policy()

    def _load_policy(self) -> None:
        try:
            with open(self.policy_path, "r") as f:
                data = yaml.safe_load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"Policy file not found: {self.policy_path}")
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML in policy file: {e}")

        if not isinstance(data, dict):
            raise ValueError("Policy file must be a YAML mapping")

        required_fields = ["version", "agent", "rules", "default"]
        missing = [field for field in required_fields if field not in data]
        if missing:
            raise ValueError(f"Policy file missing required fields: {missing}")

        if data["default"] not in ("allow", "deny"):
            raise ValueError(f"Policy default must be 'allow' or 'deny', got: {data['default']!r}")

        rules = data.get("rules", {})
        if not isinstance(rules, dict):
            raise ValueError("Policy 'rules' must be a mapping")

        self.agent: str = data["agent"]
        self.allow_list: list[str] = rules.get("allow") or []
        self.deny_list: list[str] = rules.get("deny") or []
        self.default: str = data["default"]

    def _matches_agent(self, agent: str) -> bool:
        return self.agent == "*" or self.agent == agent

    def evaluate(self, request: InterceptRequest) -> tuple[InterceptDecision, str | None]:
        if not self._matches_agent(request.agent):
            return InterceptDecision.ALLOWED, None

        if request.tool in self.deny_list:
            return InterceptDecision.BLOCKED, "policy_violation"

        if request.tool in self.allow_list:
            return InterceptDecision.ALLOWED, None

        if self.default == "deny":
            return InterceptDecision.BLOCKED, "not_in_allowlist"
        return InterceptDecision.ALLOWED, None

    def reload(self) -> None:
        self._load_policy()

    @property
    def info(self) -> dict:
        return {
            "agent": self.agent,
            "allow_count": len(self.allow_list),
            "deny_count": len(self.deny_list),
            "default": self.default,
            "policy_path": self.policy_path,
        }
