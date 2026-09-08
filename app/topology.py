from __future__ import annotations

from typing import Any, Dict, Iterable, List, Optional


def _build_identity_to_name_map(summaries: Iterable[Dict[str, Any]]) -> Dict[str, str]:
    """Return a case-insensitive identity-to-canonical-name map for all collected devices.

    Each summary contributes its own ``device`` name plus its ``hostname`` (when present)
    as keys; the canonical value is the collected device name.  This lets an LLDP-reported
    alias whose address matches a collected device's hostname resolve to the already-known
    node, avoiding dangling alias targets in the topology graph.
    """
    identity_to_name: Dict[str, str] = {}
    for summary in summaries:
        canonical = summary.get("device")
        if not canonical or not isinstance(canonical, str):
            continue
        for key in (canonical, summary.get("hostname", "")):
            if key and isinstance(key, str):
                identity_to_name.setdefault(key.lower(), canonical)
    return identity_to_name


def build_topology_graph(
    summaries: Iterable[Dict[str, Any]],
    identity_to_name: Optional[Dict[str, str]] = None,
) -> Dict[str, Any]:
    """Build a deterministic graph from collected device summaries and their discovered neighbors.

    ``identity_to_name`` is optional; when provided, a discovered neighbor whose name or
    management address matches a known identity is resolved to the canonical collected node
    name.  The original LLDP-reported alias and address are retained as edge evidence so the
    physical link is not lost.
    """
    summaries = list(summaries)
    aliases: Dict[str, str] = identity_to_name if identity_to_name is not None else _build_identity_to_name_map(summaries)
    nodes: Dict[str, Dict[str, Any]] = {}
    edges: List[Dict[str, Any]] = []

    for summary in summaries:
        name = summary.get("device")
        if not name:
            continue
        nodes[name] = {
            "vendor": summary.get("vendor", "unknown"),
            "role": summary.get("role", "unknown"),
            "neighbors": [],
            "neighbor_addresses": {},
        }

    for summary in summaries:
        source = summary.get("device")
        if not source:
            continue
        for neighbor_record in summary.get("discovered_neighbors", []) or []:
            neighbor_name = neighbor_record.get("neighbor")
            if not neighbor_name:
                continue
            neighbor_ip = neighbor_record.get("ip")
            identity_key = neighbor_ip or neighbor_name
            canonical = aliases.get(str(identity_key).lower()) if identity_key else None
            target = canonical if canonical else neighbor_name

            nodes[source]["neighbors"].append(target)
            edge: Dict[str, Any] = {"source": source, "target": target}
            if neighbor_ip:
                edge["ip"] = neighbor_ip
                nodes[source]["neighbor_addresses"][target] = neighbor_ip
            if target != neighbor_name:
                edge["alias"] = neighbor_name
            edges.append(edge)

    return {"nodes": nodes, "edges": edges}
