PHASE:
PHASE-013A-HealthScoringRemediation

STATUS:
Implemented

FILES MODIFIED:
- app/health.py
  - Removed the uptime-unknown deduction and warning for missing or `None` `uptime_days`.
  - CPU, memory, and interface-error scoring are unchanged.
  - Output shape remains `{"score": int, "warnings": [str], "critical": [str]}`.
- tests/test_health.py
  - Corrected `test_score_device_missing_data` to assert score 100 and no warnings.
  - Updated `test_score_device_multiple_issues` expected score and warning count to exclude uptime deduction.
  - Added `test_score_device_explicit_uptime_none_is_no_evidence` to prove `uptime_days: None` is also treated as no evidence.

TESTS ADDED:
- tests/test_health.py::test_score_device_explicit_uptime_none_is_no_evidence

DDR UPDATES:
UNCHANGED DD:2026-08-04

RISKS INTRODUCED:
- None.

RISKS RESOLVED:
- Missing `uptime_days` no longer produces a false health deduction or warning.

OPEN ISSUES:
- None.
