from __future__ import annotations

from typing import Any, Dict, Iterable, List


def build_topology_graph(summaries: Iterable[Dict[str, Any]]) -> Dict[str, Any]:
    """Build a deterministic graph from collected device summaries and their discovered neighbors."""
    summaries = list(summaries)
    nodes: Dict[str, Dict[str, Any]] = {}
    edges: List[Dict[str, str]] = []

    for summary in summaries:
        name = summary.get("device")
        if not name:
            continue
        nodes[name] = {
            "vendor": summary.get("vendor", "unknown"),
            "role": summary.get("role", "unknown"),
            "neighbors": [],
        }

    for summary in summaries:
        source = summary.get("device")
        if not source:
            continue
        for neighbor_record in summary.get("discovered_neighbors", []) or []:
            neighbor_name = neighbor_record.get("neighbor")
            if not neighbor_name:
                continue
            nodes[source]["neighbors"].append(neighbor_name)
            edges.append({"source": source, "target": neighbor_name})

    return {"nodes": nodes, "edges": edges}
