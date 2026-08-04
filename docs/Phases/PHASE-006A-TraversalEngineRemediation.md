PHASE:
Traversal Engine Remediation (PoC)

FILES:
- app/traversal.py
- tests/test_cli.py

ACCEPTANCE CRITERIA:
- traverse_topology() returns `visited` as a deterministically ordered list (e.g. reuse the existing `successful` BFS order, or an explicit ordered list built alongside the membership set)
- When `start` is missing from graph["nodes"], `pending` must contain all graph node names in deterministic (sorted) order, not an empty list
- `successful`, `failed`, and existing connected/cycle/branching/orphan/single-node behaviour remain unchanged
- Existing PHASE-006 tests (linear chain, cycle, branching, orphaned neighbour, single-node) continue to pass unmodified
- Regression test added/updated for missing-start pending behaviour asserting all graph nodes are returned in sorted order

CONSTRAINTS:
- No new SSH commands, no recursive collection, no concurrency, no checkpointing
- No change to function signature, call sites, or output dict keys
- No new dependencies
- Minimal fix only: correct `visited` ordering and missing-start `pending` value; do not restructure BFS algorithm or graph shape

KNOWN RISKS:
- None beyond those already carried from PHASE-006

OUTSTANDING RISKS:
- CDP/LLDP neighbour names may not match configured device names, producing orphaned/failed nodes (carried from PHASE-004/005/006)

OPEN QUESTIONS:
- None.
