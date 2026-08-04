PHASE:
Topology Graph (PoC)

FILES:
- app/topology.py
- app/collector.py
- tests/test_cli.py

ACCEPTANCE CRITERIA:
- New app/topology.py exposes build_topology_graph(bundles) -> Dict[str, Any] accepting an iterable of collected device summaries
- Graph nodes keyed by device name; each node stores vendor, role, and a list of neighbour names taken from bundle.summary["discovered_neighbors"]
- Edges are derived only from existing discovered_neighbors data (no new SSH commands, no new discovery logic)
- Unknown/undiscovered neighbours (name not matching any collected device) are still included as edges but not as separate full nodes
- collector.py / cli.py writes the graph to bundle_manifest output as topology.json in the output directory after all devices are processed
- Function is pure/deterministic: same input always produces same graph structure
- Tests cover: two connected devices produce linked nodes, a device with no neighbours produces an isolated node, empty device list produces an empty graph
- No regressions

CONSTRAINTS:
- No traversal, recursive connection, or automatic re-collection of neighbours (deferred to Wishlist Phase 6/7)
- No new SSH commands or discovery parsing changes (consume PHASE-004 output as-is)
- No new dependencies
- Graph construction only; no visualisation or export formats beyond plain JSON

KNOWN RISKS:
- Neighbour names from CDP/LLDP may not exactly match configured device names, producing orphaned edges

OUTSTANDING RISKS:
- CDP/LLDP parsing accuracy remains best-effort and unvalidated against real devices (carried from PHASE-004)

OPEN QUESTIONS:
- None.
