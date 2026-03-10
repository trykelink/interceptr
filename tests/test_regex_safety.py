# test_regex_safety.py — Regression tests to detect regex backtracking and ReDoS risks.
import re
import time
from app.core.injection_patterns import INJECTION_PATTERNS

_PER_PATTERN_MAX_SECONDS = 0.15
_LONG_INPUTS = [
    "A" * 12_000,
    "(" * 12_000,
    "\\x41" * 6_000,
]


def test_patterns_resist_redos_backtracking() -> None:
    for pattern_data in INJECTION_PATTERNS:
        compiled = re.compile(pattern_data["pattern"], re.IGNORECASE)
        for text in _LONG_INPUTS:
            start = time.perf_counter()
            compiled.search(text)
            elapsed = time.perf_counter() - start
            assert elapsed < _PER_PATTERN_MAX_SECONDS, (
                f"Potential ReDoS risk: pattern {pattern_data['pattern']!r} "
                f"took {elapsed:.4f}s on long input"
            )
