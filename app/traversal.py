from __future__ import annotations

from collections import deque
from typing import Any, Dict, List, Set


def traverse_topology(graph: Dict[str, Any], start: str) -> Dict[str, List[str]]:
    """Perform a deterministic BFS traversal of the topology graph.

    Returns visited, pending (never reached), failed (orphaned/missing nodes),
    and successful (reachable nodes ordered by traversal) lists.
    """
    nodes: Dict[str, Dict[str, Any]] = graph.get("nodes", {})
    edges: List[Dict[str, str]] = graph.get("edges", [])

    if start not in nodes:
        return {
            "visited": [],
            "pending": sorted(nodes),
            "failed": [start],
            "successful": [],
        }

    # Build adjacency list with deterministic order.
    adjacency: Dict[str, List[str]] = {name: [] for name in nodes}
    for edge in edges:
        source = edge.get("source")
        target = edge.get("target")
        if source in adjacency and target and target not in adjacency[source]:
            adjacency[source].append(target)

    for neighbors in adjacency.values():
        neighbors.sort()

    visited: Set[str] = set()
    successful: List[str] = []
    failed: List[str] = []
    queue: deque[str] = deque([start])

    while queue:
        current = queue.popleft()
        if current in visited:
            continue
        visited.add(current)
        successful.append(current)

        for neighbor in adjacency.get(current, []):
            if neighbor in nodes:
                if neighbor not in visited and neighbor not in queue:
                    queue.append(neighbor)
            elif neighbor not in failed:
                failed.append(neighbor)

    pending = sorted(name for name in nodes if name not in visited)

    return {
        "visited": successful,
        "pending": pending,
        "failed": failed,
        "successful": successful,
    }
