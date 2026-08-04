PHASE:
Topology Graph Remediation (PoC)

FILES:
- app/topology.py
- app/cli.py
- tests/test_cli.py

ACCEPTANCE CRITERIA:
- build_topology_graph() produces correct nodes AND edges when given a single-use iterable (e.g. a generator), not only a list
- cli.py's existing call site continues to work unchanged in shape (still may pass a generator or list)
- Tests cover: generator input with connected devices still produces edges (regression test for this defect)
- Existing list-based tests (connected devices, isolated node, empty graph) continue to pass
- No regressions

CONSTRAINTS:
- No new SSH commands
- No traversal, recursive connection, or visualisation logic (unchanged from PHASE-005)
- No new dependencies
- Minimal fix only: materialize the input once; do not restructure graph shape or output format

KNOWN RISKS:
- None beyond those already carried from PHASE-005

OUTSTANDING RISKS:
- CDP/LLDP neighbour names may not match configured device names, producing orphaned edges (carried from PHASE-004/005)

OPEN QUESTIONS:
- None.
