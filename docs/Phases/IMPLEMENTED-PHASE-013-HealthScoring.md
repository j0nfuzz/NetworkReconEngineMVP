PHASE:
PHASE-013-HealthScoring

STATUS:
Implemented

FILES MODIFIED:
- app/health.py (new)
  - Added `score_device_health(summary: dict) -> dict`.
  - Pure deterministic rules-based scoring over the existing `build_device_summary()` output shape.
  - Deductions: high CPU (>80), high memory (>80), any interface_errors, unknown uptime (None).
  - Missing values are treated as "no evidence" and never raise.
  - Returns `{"score": int, "warnings": [str], "critical": [str]}`; score never below 0.
- tests/test_health.py (new)
  - Added regression tests for healthy device, high CPU, high memory, interface errors, multiple issues, missing data, and deterministic output shape.

TESTS ADDED:
- tests/test_health.py::test_score_device_healthy
- tests/test_health.py::test_score_device_high_cpu
- tests/test_health.py::test_score_device_high_memory
- tests/test_health.py::test_score_device_interface_errors
- tests/test_health.py::test_score_device_multiple_issues
- tests/test_health.py::test_score_device_missing_data
- tests/test_health.py::test_score_device_output_shape

DDR UPDATES:
UNCHANGED DD:2026-08-04

RISKS INTRODUCED:
- Fixed 80% CPU/memory thresholds may not suit all device roles; acceptable for PoC, tunable later.

RISKS RESOLVED:
- None.

OPEN ISSUES:
- None.
