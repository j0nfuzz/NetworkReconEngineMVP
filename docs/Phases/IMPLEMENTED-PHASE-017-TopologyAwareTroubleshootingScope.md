PHASE:
TopologyAwareTroubleshootingScope

STATUS:
Implemented

FILES MODIFIED:
- app/scope.py (new)
- app/cli.py
- app/orchestrator.py
- tests/test_scope.py (new)
- tests/test_cli.py

TESTS ADDED/UPDATED:
- build_troubleshooting_scope includes direct neighbours
- build_troubleshooting_scope unknown target returns target only
- build_troubleshooting_scope no neighbours returns target only
- build_troubleshooting_scope ordering is deterministic
- build_troubleshooting_scope ignores empty neighbor names
- CLI --target-device limits recursive collection to scope
- CLI without --target-device preserves full collection
- CLI --target-device without topology uses target only

DDR UPDATES:
UNCHANGED DD:2026-08-05

RISKS INTRODUCED:
- Single-hop scope may omit devices needed for full root-cause context.

RISKS RESOLVED:
- Recursive collection can now be bounded to a target device and its direct neighbours.

OPEN ISSUES:
- Multi-hop / configurable depth scoping remains out of scope.
- Cross-workstation bootstrap validation still pending (operational, carried from PHASE-016B).
