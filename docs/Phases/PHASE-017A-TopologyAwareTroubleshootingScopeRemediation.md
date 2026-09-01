PHASE:
TopologyAwareTroubleshootingScopeRemediation

FILES:
app/cli.py
app/orchestrator.py
tests/test_scope.py
tests/test_cli.py

ACCEPTANCE CRITERIA:
- --target-device resolves the named device from the configured inventory as the recursive seed, not devices[0].
- If --target-device names a device absent from the config, fail with a clear error before any collection attempt.
- Resumed checkpoint pending devices are filtered against allowed_devices before being enqueued, when a scope is active.
- Regression tests cover: non-first target selection, unknown --target-device value, and resume with out-of-scope pending entries excluded.

CONSTRAINTS:
- No changes to app/scope.py's build_troubleshooting_scope() logic.
- No changes to checkpoint/resume JSON format.
- No changes to traverse_topology() or build_topology_graph() signatures.
- Preserve existing behaviour when --target-device is omitted.
- No new dependencies.

KNOWN RISKS:
- None beyond those already accepted in PHASE-017.

OUTSTANDING RISKS:
- Single-hop scoping remains intentionally incomplete for wider fault domains (carried from PHASE-017).
- Cross-workstation bootstrap validation remains pending (carried from PHASE-016B; operational, not code).

OPEN QUESTIONS:
- None.
