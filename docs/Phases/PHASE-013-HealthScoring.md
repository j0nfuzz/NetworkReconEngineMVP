PHASE:
HealthScoring

FILES:
- app/health.py
- tests/test_health.py

ACCEPTANCE CRITERIA:
- `score_device_health(summary: dict) -> dict` consumes the existing `build_device_summary()` output shape (no new fields required upstream).
- Deterministic rules-based scoring starting at 100, with fixed deductions for: high CPU (>80), high memory (>80), any `interface_errors` entries, uptime_days is None (unknown/unverifiable).
- Output shape: `{"score": int, "warnings": [str], "critical": [str]}`.
- Score never goes below 0; missing/None inputs are treated as "no evidence" (no deduction), not as errors.
- Add regression tests: healthy device (no warnings), high CPU only, high memory only, interface errors present, multiple simultaneous issues, all-missing-data device (score 100, no warnings).

CONSTRAINTS:
- No new dependencies.
- Pure function: no SSH, no CLI wiring, no I/O.
- Do not modify `app/normalization.py` or its output shape.
- Deterministic thresholds/regex only, no AI/ML.

KNOWN RISKS:
- Fixed thresholds (80% CPU/memory) may not suit all device roles; acceptable for PoC, tunable later.

OUTSTANDING RISKS:
- CLI integration of both `build_device_summary()` and `score_device_health()` remains deferred (carried from PHASE-012/012A).
- Cisco format drift and unsupported-vendor defaults remain accepted PoC risks (carried from PHASE-012).

OPEN QUESTIONS:
- None.
