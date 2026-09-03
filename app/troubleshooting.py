from __future__ import annotations

from typing import Any, Dict, List, Mapping


def build_troubleshooting_bundle(
    summary: Mapping[str, Any],
    health: Mapping[str, Any],
    raw_outputs: Mapping[str, str],
) -> Dict[str, Any]:
    """Return a deterministic AI-ready troubleshooting briefing from existing analysis results."""
    identity = {
        "hostname": summary.get("hostname") or "unknown",
        "vendor": summary.get("vendor") or "unknown",
        "model": summary.get("model") or "unknown",
        "version": summary.get("version") or "unknown",
    }

    evidence: List[str] = sorted(raw_outputs.keys())

    briefing_lines = [
        f"# Troubleshooting Briefing: {identity['hostname']}",
        "",
        f"Vendor: {identity['vendor']}",
        f"Model: {identity['model']}",
        f"Version: {identity['version']}",
        "",
        f"Health Score: {health.get('score', 100)}/100",
        "",
        "## Findings",
    ]

    warnings = list(health.get("warnings") or [])
    if warnings:
        briefing_lines.append("### Warnings")
        for warning in warnings:
            briefing_lines.append(f"- {warning}")
    else:
        briefing_lines.append("No warnings.")

    critical = list(health.get("critical") or [])
    if critical:
        briefing_lines.append("### Critical")
        for item in critical:
            briefing_lines.append(f"- {item}")

    briefing_lines.extend(["", "## Evidence Sources"])
    if evidence:
        for source in evidence:
            briefing_lines.append(f"- {source}")
    else:
        briefing_lines.append("No raw evidence referenced.")

    return {
        "hostname": identity["hostname"],
        "vendor": identity["vendor"],
        "model": identity["model"],
        "version": identity["version"],
        "health_score": int(health.get("score", 100)),
        "warnings": warnings,
        "critical": critical,
        "evidence": evidence,
        "failed_commands": list(summary.get("failed_commands") or []),
        "failed_command_details": list(summary.get("failed_command_details") or []),
        "recovered_commands": list(summary.get("recovered_commands") or []),
        "briefing": "\n".join(briefing_lines),
    }
