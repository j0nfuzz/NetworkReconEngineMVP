PHASE: PHASE-006A-TraversalEngineRemediation

STATUS: Implemented

FILES MODIFIED:
- app/traversal.py
  - `visited` now returns the deterministic BFS `successful` order instead of `list(visited)` from an unordered set.
  - Missing start-node path now returns `pending: sorted(nodes)` so all unvisited graph nodes are reported.
- tests/test_cli.py
  - Added `visited == successful` assertions to linear chain, cycle, and branching tests.
  - Updated missing-start test to assert `pending == ["A"]` and `visited == []`.

TESTS ADDED:
- Existing traversal tests updated to cover deterministic `visited` ordering.
- Existing missing-start test updated to cover correct pending behaviour.

DDR UPDATES:
- UNCHANGED DD:2026-08-04

RISKS INTRODUCED:
- None.

RISKS RESOLVED:
- Non-deterministic `visited` ordering.
- Missing start-node under-reporting pending nodes.

OPEN ISSUES:
- CDP/LLDP neighbor names may not match configured device names, producing orphaned/failed nodes (carried from PHASE-004/005/006).
