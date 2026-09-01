PHASE:
TopologyAwareTroubleshootingScopeCheckpointRemediation

STATUS:
Implemented

FILES MODIFIED:
- app/orchestrator.py
- tests/test_orchestrator.py

TESTS ADDED/UPDATED:
- allowed_devices filters resumed pending entries (also asserts emitted checkpoint state excludes them)
- allowed_devices None preserves all resumed pending entries

DDR UPDATES:
UNCHANGED DD:2026-08-05

RISKS INTRODUCED:
- None.

RISKS RESOLVED:
- Out-of-scope pending checkpoint entries no longer persist in emitted resume state.

OPEN ISSUES:
- Single-hop scoping remains intentionally incomplete (carried from PHASE-017).
- Cross-workstation bootstrap validation still pending (carried from PHASE-016B; operational).
