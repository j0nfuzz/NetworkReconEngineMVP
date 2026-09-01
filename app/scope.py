from __future__ import annotations

from typing import Any, Dict, List


def build_troubleshooting_scope(topology: Dict[str, Any], target: str) -> List[str]:
    """Return a deterministic single-hop troubleshooting scope for a target device.

    The scope contains the target device and its direct neighbours from the
    topology graph. If the target is unknown, a target-only scope is returned
    so callers can still attempt to collect it without raising.
    """
    nodes = topology.get("nodes", {}) or {}
    if target not in nodes:
        return [target]

    scope = {target}
    for neighbor in nodes[target].get("neighbors", []) or []:
        if neighbor:
            scope.add(neighbor)

    return sorted(scope)
