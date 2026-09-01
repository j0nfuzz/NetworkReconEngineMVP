PHASE:
TopologyAwareTroubleshootingScopeRemediation

STATUS:
Implemented

FILES MODIFIED:
- app/cli.py
- app/orchestrator.py
- tests/test_scope.py
- tests/test_orchestrator.py

TESTS ADDED/UPDATED:
- CLI --target-device selects non-first configured device as seed
- CLI unknown --target-device exits before collection begins
- Orchestrator allowed_devices filters resumed pending entries
- Orchestrator without allowed_devices preserves all resumed pending entries

DDR UPDATES:
UNCHANGED DD:2026-08-05

RISKS INTRODUCED:
- None beyond those already accepted in PHASE-017.

RISKS RESOLVED:
- Non-first target devices are no longer replaced by devices[0].
- Resumed checkpoints no longer enqueue out-of-scope pending devices when a scope is active.

OPEN ISSUES:
- Single-hop scoping remains intentionally incomplete (carried from PHASE-017).
- Cross-workstation bootstrap validation still pending (carried from PHASE-016B; operational).
