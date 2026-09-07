PHASE:
PHASE-087A-TopologyAliasBackEdgeRemediation

FILES:
- app/topology.py
- app/orchestrator.py

ACCEPTANCE CRITERIA:
- When building topology.json, a discovered neighbour whose resolved IP/hostname matches an already-collected device's identity (name or hostname) must produce an edge whose target is the canonical collected node's name, not the LLDP-reported alias name.
- The LLDP-reported alias name and management address must still be retained as edge evidence (e.g. an "alias" field on the edge) so the physical connection description (e.g. "LAG 2 to `<LOCATION>`") is not lost.
- topology.json must not contain a dangling node reference: every edge target must resolve to a node key present in `nodes`.
- Regression test proves an alias neighbour (matching an already-collected device's hostname) produces an edge targeting the canonical node, not a new/dangling node.
- Regression test proves a genuinely distinct neighbour (no address match) is unaffected: edge target is unchanged and still equals the neighbour's own name.

CONSTRAINTS:
- Do not modify discovery, LLDP parsing, classification, queueing, credential propagation, streaming, provenance, or the PHASE-084 identity-probe gate.
- Do not modify PHASE-087's collection-path deduplication logic (`_device_identity_set`/`known_identities` in app/orchestrator.py and app/parallel_collector.py); it is correct and field-validated. Only expose or reuse identity information needed for topology resolution.
- `build_topology_graph()` currently receives only `summaries` (list of per-device summary dicts); if identity-to-canonical-name resolution requires additional input, prefer passing it as an additional optional parameter rather than changing the summary schema.

KNOWN RISKS:
- Resolving alias targets requires matching neighbour IP against collected devices' hostnames; devices with multiple management addresses may still produce an unresolved (name-only) edge if the LLDP-reported address differs from the address used to reach the device — this is the same accepted limitation as PHASE-087, not a new one.

OUTSTANDING RISKS:
- SW3-class third-hop hardware remains unproven in any bundle to date; unaffected by this phase.

OPEN QUESTIONS:
- None.
