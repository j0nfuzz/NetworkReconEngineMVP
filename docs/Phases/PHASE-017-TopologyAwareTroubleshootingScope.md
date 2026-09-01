PHASE:
TopologyAwareTroubleshootingScope

FILES:
app/scope.py
app/cli.py
tests/test_scope.py

ACCEPTANCE CRITERIA:
- build_troubleshooting_scope(topology, target) returns {target} plus its direct neighbours only, deterministic ordering.
- Unknown target device returns an empty/target-only scope without raising.
- CLI --target-device flag limits recursive collection's initial pending set to the computed scope; omitting it preserves current full-estate behaviour.
- No changes to traverse_topology() or build_topology_graph() signatures.

CONSTRAINTS:
- No new dependencies.
- Reuse existing topology.json structure from PHASE-005A.
- Must not alter checkpoint/resume format.

KNOWN RISKS:
- Single-hop scope may omit devices needed for full root-cause context.

OUTSTANDING RISKS:
- Cross-workstation bootstrap validation still pending (carried from PHASE-016B; operational, not code).

OPEN QUESTIONS:
- Should scope depth become configurable in a later phase?
