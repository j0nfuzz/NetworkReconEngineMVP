from __future__ import annotations

from collections import deque
from typing import Any, Dict, List, Set


def build_troubleshooting_scope(
    topology: Dict[str, Any], target: str, hops: int = 1
) -> List[str]:
    """Return a deterministic troubleshooting scope for a target device.

    Performs a breadth-first traversal out to *hops* edges from *target*,
    returning the sorted union of all nodes visited within that radius.  The
    traversal is cycle-safe and terminates on loops.  If the target is unknown,
    a target-only scope is returned so callers can still attempt to collect it
    without raising.
    """
    nodes = topology.get("nodes", {}) or {}
    if target not in nodes:
        return [target]

    if hops <= 0:
        return [target]

    visited: Set[str] = {target}
    queue: deque[tuple[str, int]] = deque([(target, 0)])

    while queue:
        current, distance = queue.popleft()
        if distance >= hops:
            continue
        for neighbor in nodes.get(current, {}).get("neighbors", []) or []:
            if not neighbor:
                continue
            if neighbor in visited:
                continue
            visited.add(neighbor)
            queue.append((neighbor, distance + 1))

    return sorted(visited)
