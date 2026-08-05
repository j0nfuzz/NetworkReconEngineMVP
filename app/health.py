from __future__ import annotations

from typing import Any, Dict, List


def score_device_health(summary: Dict[str, Any]) -> Dict[str, Any]:
    """Return a deterministic health score and issue lists from a normalized summary."""
    score = 100
    warnings: List[str] = []
    critical: List[str] = []

    cpu = summary.get("cpu")
    if isinstance(cpu, (int, float)) and cpu > 80:
        warnings.append("CPU utilisation high")
        score -= 15

    memory = summary.get("memory")
    if isinstance(memory, (int, float)) and memory > 80:
        warnings.append("Memory utilisation high")
        score -= 15

    interface_errors = summary.get("interface_errors") or []
    if interface_errors:
        warnings.append(f"Interface errors detected on {', '.join(interface_errors)}")
        score -= 10

    return {
        "score": max(score, 0),
        "warnings": warnings,
        "critical": critical,
    }
