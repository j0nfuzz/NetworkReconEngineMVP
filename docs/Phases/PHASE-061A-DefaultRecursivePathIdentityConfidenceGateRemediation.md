PHASE:
DefaultRecursivePathIdentityConfidenceGateRemediation

FILES:
app/orchestrator.py
tests/test_orchestrator.py

ACCEPTANCE CRITERIA:
- When _probe_identity() retains an existing higher-confidence identity, device.vendor is synchronized to that identity's vendor if device.vendor was "auto" or "unknown".
- No change to overwrite-branch behaviour (probe wins when strictly more confident).
- New regression test proves vendor="auto" + high-confidence existing identity + lower-confidence probe resolves device.vendor to the existing identity's vendor.
- All PHASE-061 tests continue to pass unmodified in behaviour.

CONSTRAINTS:
- No changes to app/collector.py, app/parallel_collector.py, app/discovery.py, app/vendor_profiles.py, app/health.py, app/ssh_client.py, or CLI.
- No confidence-gating algorithm changes.
- Minimise delta to the single missing sync assignment plus one test.

KNOWN RISKS:
- None beyond PHASE-061's existing known risk (one extra SSH connection per auto/unknown device).

OUTSTANDING RISKS:
- The "unreachable" field symptom remains a separate, uninvestigated issue outside this phase's scope.

OPEN QUESTIONS:
- None.
