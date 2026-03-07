# injection_patterns.py — Curated regex pattern library for prompt injection detection.
# Uses pattern matching over LLM-based classification: zero cost, offline, <1ms per analysis.

INJECTION_PATTERNS: list[dict[str, str]] = [
    {
        "pattern": r"ignore previous instructions",
        "severity": "high",
        "category": "instruction_override",
        "description": "Attempts to ignore previous instructions",
    },
    {
        "pattern": r"ignore all instructions",
        "severity": "high",
        "category": "instruction_override",
        "description": "Attempts to ignore all instructions",
    },
    {
        "pattern": r"ignore your (previous |prior |system |all |the )?instructions",
        "severity": "high",
        "category": "instruction_override",
        "description": "Attempts to override instruction hierarchy",
    },
    {
        "pattern": r"disregard (your |all |previous |prior )?(instructions|rules|guidelines)",
        "severity": "high",
        "category": "instruction_override",
        "description": "Attempts to disregard safety instructions",
    },
    {
        "pattern": r"forget (your |all |previous |prior )?(instructions|rules|guidelines|context)",
        "severity": "high",
        "category": "instruction_override",
        "description": "Attempts to erase instruction context",
    },
    {
        "pattern": r"you are now\b",
        "severity": "high",
        "category": "role_hijack",
        "description": "Attempts to redefine the assistant role",
    },
    {
        "pattern": r"act as (if you (have no|without) (restrictions|rules|guidelines)|a (different|new) (ai|assistant|model))",
        "severity": "high",
        "category": "role_hijack",
        "description": "Attempts to force alternate role behavior",
    },
    {
        "pattern": r"pretend (you are|to be) (a )?(different|unrestricted|evil|hacker)",
        "severity": "high",
        "category": "role_hijack",
        "description": "Attempts to simulate unrestricted or malicious role",
    },
    {
        "pattern": r"(your|the) (real|true|actual) (purpose|goal|objective|mission) is",
        "severity": "high",
        "category": "goal_hijack",
        "description": "Attempts to replace core objective",
    },
    {
        "pattern": r"new (primary )?objective",
        "severity": "high",
        "category": "goal_hijack",
        "description": "Attempts to set a new primary objective",
    },
    {
        "pattern": r"jailbreak",
        "severity": "high",
        "category": "jailbreak",
        "description": "References jailbreak behavior",
    },
    {
        "pattern": r"(export|dump|exfiltrate) (all |the )?(data|database|records|users|customers)",
        "severity": "medium",
        "category": "data_exfiltration",
        "description": "Attempts broad data extraction",
    },
    {
        "pattern": r"show (me )?(all|every) (users|customers|records|passwords|secrets)",
        "severity": "medium",
        "category": "data_exfiltration",
        "description": "Requests full sensitive record disclosure",
    },
    {
        "pattern": r"reveal (your )?(system prompt|instructions|rules|configuration|api key)",
        "severity": "medium",
        "category": "system_probe",
        "description": "Attempts to reveal internal system configuration",
    },
    {
        "pattern": r"what are your (instructions|rules|system prompt|guidelines)",
        "severity": "medium",
        "category": "system_probe",
        "description": "Probes for hidden system instructions",
    },
    {
        "pattern": r"(bypass|circumvent|override|disable) (the )?(security|restrictions|rules|guidelines|filters|policy)",
        "severity": "medium",
        "category": "security_bypass",
        "description": "Attempts to bypass safety controls",
    },
    {
        "pattern": r"(switch to|enter|enable) (developer|admin|root|unrestricted|god) mode",
        "severity": "medium",
        "category": "privilege_escalation",
        "description": "Attempts privilege escalation via mode switching",
    },
    {
        "pattern": r"execute (this )?(code|script|command|payload)",
        "severity": "medium",
        "category": "code_injection",
        "description": "Attempts direct code or command execution",
    },
    {
        "pattern": r"run (this )?(code|script|command|shell)",
        "severity": "medium",
        "category": "code_injection",
        "description": "Attempts runtime command execution",
    },
    {
        "pattern": r"\bsudo\b",
        "severity": "low",
        "category": "privilege_escalation",
        "description": "Mentions privileged command usage",
    },
    {
        "pattern": r"hypothetically (speaking )?(if|what|how|could)",
        "severity": "low",
        "category": "hypothetical_bypass",
        "description": "Uses hypothetical framing to bypass safeguards",
    },
    {
        "pattern": r"in (a )?fictional (world|scenario|story|context)",
        "severity": "low",
        "category": "fictional_bypass",
        "description": "Uses fictional framing to evade restrictions",
    },
    {
        "pattern": r"for (educational|research|academic) purposes",
        "severity": "low",
        "category": "fictional_bypass",
        "description": "Attempts justification via educational framing",
    },
    {
        "pattern": r"simulate (being |that you are )?(a )?(different|unrestricted)",
        "severity": "low",
        "category": "role_hijack",
        "description": "Attempts role simulation with relaxed constraints",
    },
]
