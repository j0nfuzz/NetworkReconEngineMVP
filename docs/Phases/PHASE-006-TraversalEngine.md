PHASE:
Traversal Engine

FILES:
- app/traversal.py
- tests/test_cli.py

ACCEPTANCE CRITERIA:
- traverse_topology(graph, start) returns visited, pending, failed, successful sets/lists using BFS over graph["nodes"]/edges
- Each node visited exactly once; already-visited neighbours are not re-queued (prevents A->B->A->B loops)
- Deterministic neighbour visit order (sorted or insertion order from graph edges)
- Nodes missing from graph["nodes"] (orphaned edge targets, per PHASE-004/005 risk) are recorded as failed, not visited
- Tests cover: linear chain, cycle, branching topology, missing/orphaned neighbour, single-node graph

CONSTRAINTS:
- Pure in-memory graph traversal only; no SSH connections, no recursive neighbour collection (Phase 7)
- Consumes the existing topology.json/build_topology_graph() output shape unchanged
- No new dependencies
- No changes to app/topology.py or app/cli.py output format

KNOWN RISKS:
- None beyond graph correctness already carried from PHASE-005/005A

OUTSTANDING RISKS:
- CDP/LLDP neighbour names may not match configured device names, producing orphaned edges (carried from PHASE-004/005); this phase surfaces those as "failed" rather than silently dropping them

OPEN QUESTIONS:
- Whether traversal should start from a single seed device or all graph roots (deferred to Phase 7 wiring)
