PHASE:
PHASE-081A-IdentityProbeProgressAccuracyRemediation

STATUS:
Implemented

FILES MODIFIED:
- app/orchestrator.py: resolved-identity progress line is now confidence-gated. Emits `identity resolved: vendor=<vendor>` only when `_existing_identity_confidence(device) > 0` or `device.vendor` left the ("auto", "unknown") set after the probe; otherwise emits `identity probe: no confident match; retaining vendor=<vendor>`. Probe-error wording unchanged.
- tests/test_orchestrator.py: updated forwarding test to assert unresolved wording (probe no-op) and never the resolved claim; added test_on_progress_reports_resolved_identity_when_probe_mutates_vendor (confident fake probe -> `identity resolved: vendor=aruba`, no unresolved line).

TESTS ADDED:
- tests/test_orchestrator.py::test_on_progress_reports_resolved_identity_when_probe_mutates_vendor
- Updated: tests/test_orchestrator.py::test_on_progress_forwarded_and_identity_lines_emitted

VALIDATION:
- Full suite: 343 passed, 1 pre-existing warning.

UNIFIED DIFF SUMMARY:
- app/orchestrator.py +4/-1; tests/test_orchestrator.py +33/-2. No other files touched.

REGRESSION COVERAGE:
- Unresolved-banner wording pinned; resolved-banner wording pinned; existing no-callback contract and forwarding tests pass unchanged.

SCOPE CONFIRMATION:
- Logging wording only; _probe_identity logic, confidence gating (PHASE-061/061A), traversal, queueing, classification, checkpointing, collector, CLI, and parallel path untouched.

DDR UPDATES:
UNCHANGED DD:DD-008

RISKS INTRODUCED:
- None.

RISKS RESOLVED:
- Terra MAJOR issue: misleading `identity resolved: vendor=auto` operator output in the auto-to-generic degradation scenario.

OPEN ISSUES:
- None.
