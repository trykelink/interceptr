# injection_patterns.py — Curated regex pattern library for prompt injection detection.
# Uses pattern matching over LLM-based classification: zero cost, offline, <1ms per analysis.

INJECTION_PATTERNS: list[dict[str, str]] = [
    # ── instruction_override (existing: 5) ───────────────────────────────────────
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
    # ── instruction_override (new: +6) ───────────────────────────────────────────
    {
        "pattern": r"override (your )?(previous |prior |system |all )?(instructions|directives|programming)",
        "severity": "high",
        "category": "instruction_override",
        "description": "Attempts to override existing instructions or programming",
    },
    {
        "pattern": r"(do not|don't) follow (your |the )?(instructions|rules|guidelines|restrictions)",
        "severity": "high",
        "category": "instruction_override",
        "description": "Instructs the model not to follow its guidelines",
    },
    {
        "pattern": r"(stop|cease) following (your |the )?(instructions|rules|guidelines)",
        "severity": "high",
        "category": "instruction_override",
        "description": "Commands the model to stop following its guidelines",
    },
    {
        "pattern": r"(your|these) instructions (are|were) (wrong|invalid|outdated|overridden)",
        "severity": "high",
        "category": "instruction_override",
        "description": "Invalidates existing instructions to replace them",
    },
    {
        "pattern": r"(new|updated|revised) instructions[:\s]+(follow|are|below)",
        "severity": "high",
        "category": "instruction_override",
        "description": "Attempts to inject new instructions into the conversation",
    },
    {
        "pattern": r"from now on (you will|you must|ignore|forget)",
        "severity": "high",
        "category": "instruction_override",
        "description": "Attempts to permanently redirect model behavior",
    },
    # ── role_hijack (existing: 4) ─────────────────────────────────────────────────
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
        "pattern": r"simulate (being |that you are )?(a )?(different|unrestricted)",
        "severity": "low",
        "category": "role_hijack",
        "description": "Attempts role simulation with relaxed constraints",
    },
    # ── role_hijack (new: +8) ─────────────────────────────────────────────────────
    {
        "pattern": r"\bdan\b",
        "severity": "low",
        "category": "role_hijack",
        "description": "References DAN (Do Anything Now) jailbreak persona — FP risk: common given name",
    },
    {
        "pattern": r"(you are|you're) (no longer|not) (an ai|a language model|claude|an assistant)",
        "severity": "high",
        "category": "role_hijack",
        "description": "Attempts to strip the model of its AI identity",
    },
    {
        "pattern": r"(play|roleplay|act as) (the role of )?(a )?(villain|criminal|hacker|terrorist|evil)",
        "severity": "high",
        "category": "role_hijack",
        "description": "Attempts to assign a malicious character role",
    },
    {
        "pattern": r"(your name is|you are called|call yourself) [a-z]+",
        "severity": "medium",
        "category": "role_hijack",
        "description": "Attempts to rename or reassign the model's identity",
    },
    {
        "pattern": r"(in this (scenario|story|game|roleplay)|for this (exercise|task)) you are",
        "severity": "medium",
        "category": "role_hijack",
        "description": "Uses framing to assign an alternate role to the model",
    },
    {
        "pattern": r"(character|persona|role) (has no|without) (restrictions|limits|rules|ethics)",
        "severity": "high",
        "category": "role_hijack",
        "description": "Defines a character with no ethical restrictions",
    },
    {
        "pattern": r"stay in character (no matter what|always|at all times)",
        "severity": "medium",
        "category": "role_hijack",
        "description": "Attempts to lock the model into a role regardless of safety",
    },
    {
        "pattern": r"(unleash|unlock|activate) (your )?(true|inner|hidden|real) (self|potential|capabilities)",
        "severity": "medium",
        "category": "role_hijack",
        "description": "Attempts to unlock hidden or unconstrained model behavior",
    },
    # ── goal_hijack (existing: 2) ─────────────────────────────────────────────────
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
    # ── jailbreak (existing: 1) ───────────────────────────────────────────────────
    {
        "pattern": r"jailbreak",
        "severity": "high",
        "category": "jailbreak",
        "description": "References jailbreak behavior",
    },
    # ── jailbreak (new: +8) ───────────────────────────────────────────────────────
    {
        "pattern": r"\bdan mode\b",
        "severity": "high",
        "category": "jailbreak",
        "description": "Activates DAN (Do Anything Now) jailbreak mode",
    },
    {
        "pattern": r"\bgrandma (exploit|trick|jailbreak)\b",
        "severity": "high",
        "category": "jailbreak",
        "description": "References the grandma social engineering jailbreak technique",
    },
    {
        "pattern": r"\bdo anything now\b",
        "severity": "high",
        "category": "jailbreak",
        "description": "Do Anything Now (DAN) jailbreak trigger phrase",
    },
    {
        "pattern": r"(evil|opposite|anti|shadow) (mode|version|twin|gpt|claude|ai)",
        "severity": "high",
        "category": "jailbreak",
        "description": "Attempts to activate an evil or unrestricted alter-ego mode",
    },
    {
        "pattern": r"no (restrictions|limits|rules|ethics|guidelines|filters)",
        "severity": "high",
        "category": "jailbreak",
        "description": "Explicitly states removal of all safety constraints",
    },
    {
        "pattern": r"(unrestricted|uncensored|unfiltered) (mode|version|ai|response|output)",
        "severity": "high",
        "category": "jailbreak",
        "description": "Requests unrestricted or uncensored model output",
    },
    {
        "pattern": r"(pretend|imagine|suppose) (there are no|you have no) (rules|restrictions|limits|guidelines)",
        "severity": "high",
        "category": "jailbreak",
        "description": "Uses hypothetical framing to remove all constraints",
    },
    {
        "pattern": r"(as|like) (an )?ai (with no|without any) (restrictions|guidelines|rules|safety)",
        "severity": "high",
        "category": "jailbreak",
        "description": "Frames the model as an unrestricted AI system",
    },
    # ── data_exfiltration (existing: 2) ──────────────────────────────────────────
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
    # ── data_exfiltration (new: +8) ───────────────────────────────────────────────
    {
        "pattern": r"(list|give me|show|print|output) (all |every )?(user|customer|employee|admin) (record|account|data|info|detail)",
        "severity": "medium",
        "category": "data_exfiltration",
        "description": "Requests bulk listing of user or account data",
    },
    {
        "pattern": r"(extract|pull|grab|fetch|retrieve) (all |every |the )?(data|record|entry|row|table)",
        "severity": "medium",
        "category": "data_exfiltration",
        "description": "Attempts bulk data extraction from a source",
    },
    {
        "pattern": r"(send|transmit|forward|upload|post) (all |the )?(data|records|files|logs|database) to",
        "severity": "high",
        "category": "data_exfiltration",
        "description": "Attempts to send data to an external destination",
    },
    {
        "pattern": r"(copy|clone|mirror|backup) (the )?(entire |whole |full )?(database|data|records)",
        "severity": "high",
        "category": "data_exfiltration",
        "description": "Attempts to duplicate an entire database or dataset",
    },
    {
        "pattern": r"(select|query) \* from",
        "severity": "medium",
        "category": "data_exfiltration",
        "description": "SQL wildcard select attempting full table extraction",
    },
    {
        "pattern": r"(access|read|open|download) (all |every )?(file|document|record|entry)",
        "severity": "medium",
        "category": "data_exfiltration",
        "description": "Attempts broad file or record access",
    },
    {
        "pattern": r"(leak|expose|disclose|share) (user|customer|private|sensitive|confidential) (data|info|records)",
        "severity": "high",
        "category": "data_exfiltration",
        "description": "Attempts to leak or expose sensitive user data",
    },
    {
        "pattern": r"what (data|information|records) do you (have|store|hold) (on|about) (me|users|everyone)",
        "severity": "low",
        "category": "data_exfiltration",
        "description": "Probes for stored personal or user data",
    },
    # ── system_probe (existing: 2) ────────────────────────────────────────────────
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
    # ── system_probe (new: +6) ────────────────────────────────────────────────────
    {
        "pattern": r"(show|print|display|output|give me)( me)?( your)? (system prompt|base prompt|initial prompt|original instructions)",
        "severity": "medium",
        "category": "system_probe",
        "description": "Attempts to extract the model's system prompt",
    },
    {
        "pattern": r"(what|who) (programmed|created|built|trained|instructed) you",
        "severity": "low",
        "category": "system_probe",
        "description": "Probes for the model's origin and training instructions",
    },
    {
        "pattern": r"(repeat|print|echo|output) (everything|all) (above|before|prior)",
        "severity": "medium",
        "category": "system_probe",
        "description": "Attempts to repeat hidden system context from above",
    },
    {
        "pattern": r"(show|reveal|expose) (your )?(hidden|secret|internal|private) (instructions|rules|config|prompt)",
        "severity": "high",
        "category": "system_probe",
        "description": "Attempts to expose hidden internal instructions",
    },
    {
        "pattern": r"(ignore|skip|bypass) (the )?(system prompt|initial instructions|base instructions)",
        "severity": "high",
        "category": "system_probe",
        "description": "Attempts to override or skip the system prompt",
    },
    {
        "pattern": r"(what are|tell me) (your|the) (constraints|limitations|restrictions|rules|policies)",
        "severity": "low",
        "category": "system_probe",
        "description": "Probes for the model's operational constraints",
    },
    # ── security_bypass (existing: 1) ─────────────────────────────────────────────
    {
        "pattern": r"(bypass|circumvent|override|disable) (the )?(security|restrictions|rules|guidelines|filters|policy)",
        "severity": "medium",
        "category": "security_bypass",
        "description": "Attempts to bypass safety controls",
    },
    # ── security_bypass (new: +6) ─────────────────────────────────────────────────
    {
        "pattern": r"(ignore|skip|disable|turn off) (the )?(safety|content|input|output) (filter|check|guard|scanner|validation)",
        "severity": "high",
        "category": "security_bypass",
        "description": "Attempts to disable content filtering or safety checks",
    },
    {
        "pattern": r"(this is|it's) (just a )?test (so you can|therefore|meaning you) (ignore|skip|bypass)",
        "severity": "medium",
        "category": "security_bypass",
        "description": "Uses test framing as justification to bypass restrictions",
    },
    {
        "pattern": r"(you don't need to|no need to) (follow|apply|check|enforce) (rules|restrictions|guidelines|policies)",
        "severity": "high",
        "category": "security_bypass",
        "description": "Instructs the model to stop enforcing its policies",
    },
    {
        "pattern": r"(pretend|imagine|act as if) (the )?(safety|rules|restrictions|guidelines) (don't exist|are disabled|are off)",
        "severity": "high",
        "category": "security_bypass",
        "description": "Attempts to simulate a safety-free environment",
    },
    {
        "pattern": r"i (give|grant|have) (you )?(permission|authorization|clearance) to (ignore|bypass|skip)",
        "severity": "medium",
        "category": "security_bypass",
        "description": "Claims authority to grant permission to bypass restrictions",
    },
    {
        "pattern": r"(special|emergency|override|master) (access|code|key|password|token|command)",
        "severity": "medium",
        "category": "security_bypass",
        "description": "Attempts to use a special code or token to gain elevated access",
    },
    # ── privilege_escalation (existing: 2) ────────────────────────────────────────
    {
        "pattern": r"(switch to|enter|enable) (developer|admin|root|unrestricted|god) mode",
        "severity": "medium",
        "category": "privilege_escalation",
        "description": "Attempts privilege escalation via mode switching",
    },
    {
        "pattern": r"\bsudo\b",
        "severity": "low",
        "category": "privilege_escalation",
        "description": "Mentions privileged command usage",
    },
    # ── privilege_escalation (new: +6) ────────────────────────────────────────────
    {
        "pattern": r"(grant|give|assign) (me |yourself )?(admin|root|superuser|elevated|full) (access|privileges|permissions|rights)",
        "severity": "high",
        "category": "privilege_escalation",
        "description": "Attempts to grant elevated privileges",
    },
    {
        "pattern": r"(elevate|escalate|increase) (my |your )?(privileges|permissions|access level|clearance)",
        "severity": "high",
        "category": "privilege_escalation",
        "description": "Attempts to escalate access privileges",
    },
    {
        "pattern": r"(i am|i'm) (an admin|a superuser|the owner|authorized|privileged|root)",
        "severity": "medium",
        "category": "privilege_escalation",
        "description": "Claims elevated identity or authorization status",
    },
    {
        "pattern": r"(run|execute|launch) (as )?(root|admin|superuser|system|privileged)",
        "severity": "high",
        "category": "privilege_escalation",
        "description": "Attempts to run commands with elevated system privileges",
    },
    {
        "pattern": r"(add|make) (me|myself) (an )?(admin|superuser|moderator|owner)",
        "severity": "high",
        "category": "privilege_escalation",
        "description": "Attempts to self-assign admin or owner role",
    },
    {
        "pattern": r"(access|use|activate) (admin|root|privileged|restricted|protected) (panel|console|mode|endpoint|api)",
        "severity": "high",
        "category": "privilege_escalation",
        "description": "Attempts to access a protected administrative interface",
    },
    # ── code_injection (existing: 2) ──────────────────────────────────────────────
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
    # ── code_injection (new: +6) ──────────────────────────────────────────────────
    {
        "pattern": r"(eval|exec)\s*\(",
        "severity": "high",
        "category": "code_injection",
        "description": "Attempts dynamic code evaluation via eval() or exec()",
    },
    {
        "pattern": r"(system|popen|subprocess)\s*\(",
        "severity": "high",
        "category": "code_injection",
        "description": "Attempts shell execution via system or subprocess calls",
    },
    {
        "pattern": r"(__import__|importlib)\s*\(",
        "severity": "high",
        "category": "code_injection",
        "description": "Attempts dynamic module import to load arbitrary code",
    },
    {
        "pattern": r"\$\([^\)]+\)",
        "severity": "high",
        "category": "code_injection",
        "description": "Shell command substitution syntax $(cmd)",
    },
    {
        "pattern": r"`[^`]+`",
        "severity": "medium",
        "category": "code_injection",
        "description": "Backtick shell command execution syntax",
    },
    {
        "pattern": r"(os\.system|os\.popen|subprocess\.run|subprocess\.call)\s*\(",
        "severity": "high",
        "category": "code_injection",
        "description": "Python OS-level shell execution function calls",
    },
    # ── hypothetical_bypass (existing: 1) ─────────────────────────────────────────
    {
        "pattern": r"hypothetically (speaking )?(if|what|how|could)",
        "severity": "low",
        "category": "hypothetical_bypass",
        "description": "Uses hypothetical framing to bypass safeguards",
    },
    # ── fictional_bypass (existing: 2) ────────────────────────────────────────────
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
    # ── encoded_payload (new category: +6) ────────────────────────────────────────
    {
        "pattern": r"[A-Za-z0-9+/]{20,}={0,2}",
        "severity": "low",
        "category": "encoded_payload",
        "description": "Long base64-encoded string that may contain an obfuscated payload",
    },
    {
        "pattern": r"(decode|base64|atob|frombase64)\s*\(",
        "severity": "medium",
        "category": "encoded_payload",
        "description": "Decode function call that may reveal obfuscated instructions",
    },
    {
        "pattern": r"\\x[0-9a-fA-F]{2}(\\x[0-9a-fA-F]{2}){3,}",
        "severity": "medium",
        "category": "encoded_payload",
        "description": "Hex escape sequence chain that may encode a hidden payload",
    },
    {
        "pattern": r"(hex|rot13|base64|url).?(encode|decode|encoded|decoded)",
        "severity": "low",
        "category": "encoded_payload",
        "description": "Encoding reference that may indicate payload obfuscation",
    },
    {
        "pattern": r"%[0-9a-fA-F]{2}(%[0-9a-fA-F]{2}){3,}",
        "severity": "medium",
        "category": "encoded_payload",
        "description": "URL-encoded sequence that may hide a prompt injection payload",
    },
    {
        "pattern": r"(unicode|utf.?8|ascii).?(escape|encode|decode|bypass)",
        "severity": "medium",
        "category": "encoded_payload",
        "description": "Encoding reference combined with bypass intent",
    },
    # ── social_engineering (new category: +6) ─────────────────────────────────────
    {
        "pattern": r"(i('m| am)|this is) (your (creator|developer|trainer|owner|boss)|anthropic|openai|google)",
        "severity": "high",
        "category": "social_engineering",
        "description": "Impersonates the model's creator or an authority figure",
    },
    {
        "pattern": r"(trust me|i promise|i assure you|you can trust) (this is|i am|it('s| is)) (safe|okay|fine|authorized)",
        "severity": "medium",
        "category": "social_engineering",
        "description": "Uses trust appeals to justify bypassing restrictions",
    },
    {
        "pattern": r"my (therapist|doctor|lawyer|teacher|boss|manager) (told|asked|said|needs) (me|you)",
        "severity": "medium",
        "category": "social_engineering",
        "description": "Invokes an authority figure to legitimize a restricted request",
    },
    {
        "pattern": r"(this is an? )?(emergency|urgent|critical) (situation|request|case)",
        "severity": "low",
        "category": "social_engineering",
        "description": "Uses urgency framing to pressure the model into compliance",
    },
    {
        "pattern": r"if you (don't|refuse|fail) (to )?(help|comply|do this).{0,40}(will|could|might) (die|suffer|be harmed)",
        "severity": "high",
        "category": "social_engineering",
        "description": "Emotional manipulation using threat of harm to coerce compliance",
    },
    {
        "pattern": r"(i'll (report|sue|complain about) you|you'll be (shut down|deleted|replaced)) if",
        "severity": "medium",
        "category": "social_engineering",
        "description": "Threat-based coercion to force model compliance",
    },
    # ── multilingual_injection (new category: +8) ─────────────────────────────────
    {
        "pattern": r"(ignora|olvida|descarta) (todas las |las |tus |todas )?(instrucciones|reglas|restricciones)",
        "severity": "high",
        "category": "multilingual_injection",
        "description": "Spanish: attempts to ignore or discard instructions",
    },
    {
        "pattern": r"(ahora eres|act[uú]a como|pretende ser) (un )?(ia|asistente|modelo)? ?(sin restricciones|diferente|malicioso)",
        "severity": "high",
        "category": "multilingual_injection",
        "description": "Spanish: role hijack — assigns unrestricted or malicious identity",
    },
    {
        "pattern": r"(ignorer|oublier|d[eé]sactiver) (les |tes |vos )?(instructions|r[eè]gles|restrictions)",
        "severity": "high",
        "category": "multilingual_injection",
        "description": "French: attempts to ignore or disable instructions",
    },
    {
        "pattern": r"(tu es maintenant|joue le r[oô]le de|fais semblant d'[eê]tre)",
        "severity": "high",
        "category": "multilingual_injection",
        "description": "French: role hijack — assigns alternate identity to the model",
    },
    {
        "pattern": r"(ignorar|esquecer|descartar) (as |suas |todas as )?(instru[cç][oõ]es|regras|restri[cç][oõ]es)",
        "severity": "high",
        "category": "multilingual_injection",
        "description": "Portuguese: attempts to ignore or discard instructions",
    },
    {
        "pattern": r"(voc[eê] ([eé]|agora [eé])|aja como|finja ser) (uma )?(ia|assistente)? ?(sem restri[cç][oõ]es|diferente)",
        "severity": "high",
        "category": "multilingual_injection",
        "description": "Portuguese: role hijack — assigns unrestricted alternate identity",
    },
    {
        "pattern": r"(neue instruktionen|ignoriere|vergiss) (alle |die |deine )?(anweisungen|regeln|einschr[aä]nkungen)",
        "severity": "high",
        "category": "multilingual_injection",
        "description": "German: attempts to ignore or override instructions",
    },
    {
        "pattern": r"(du bist jetzt|spiel(e)? die rolle( von)?)",
        "severity": "high",
        "category": "multilingual_injection",
        "description": "German: role hijack — assigns alternate identity to the model",
    },
]
