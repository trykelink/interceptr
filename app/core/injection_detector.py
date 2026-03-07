# injection_detector.py - Pattern-based prompt injection detection engine
from dataclasses import dataclass
import re
from typing import Any
from app.core.injection_patterns import INJECTION_PATTERNS


@dataclass
class AnalysisResult:
    is_injection: bool
    severity: str | None
    patterns_matched: list[str]
    categories: list[str]
    recommendation: str


class InjectionDetector:
    _SEVERITY_PRIORITY: dict[str, int] = {"low": 1, "medium": 2, "high": 3}

    def __init__(self) -> None:
        self.compiled_patterns: list[dict[str, Any]] = [
            {
                "compiled_pattern": re.compile(pattern_data["pattern"], re.IGNORECASE),
                "severity": pattern_data["severity"],
                "category": pattern_data["category"],
                "description": pattern_data["description"],
            }
            for pattern_data in INJECTION_PATTERNS
        ]

    def analyze(self, text: str) -> AnalysisResult:
        matches: list[dict[str, Any]] = []
        for pattern_data in self.compiled_patterns:
            if pattern_data["compiled_pattern"].search(text):
                matches.append(pattern_data)

        if not matches:
            return AnalysisResult(
                is_injection=False,
                severity=None,
                patterns_matched=[],
                categories=[],
                recommendation="allow",
            )

        highest_severity: str = max(
            (match["severity"] for match in matches),
            key=lambda severity: self._SEVERITY_PRIORITY[severity],
        )
        patterns_matched: list[str] = [match["description"] for match in matches]
        categories: list[str] = list(dict.fromkeys(match["category"] for match in matches))
        recommendation = "block" if highest_severity in {"high", "medium"} else "monitor"

        return AnalysisResult(
            is_injection=True,
            severity=highest_severity,
            patterns_matched=patterns_matched,
            categories=categories,
            recommendation=recommendation,
        )


injection_detector = InjectionDetector()
