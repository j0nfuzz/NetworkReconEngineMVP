PHASE:
PHASE-013A-HealthScoringRemediation

FILES:
- app/health.py
- tests/test_health.py

ACCEPTANCE CRITERIA:
- `score_device_health()` treats a missing or `None` `uptime_days` as no evidence: no deduction, no warning.
- All other deduction rules (CPU >80, memory >80, interface_errors present) are unchanged.
- `score_device_health({})` returns `{"score": 100, "warnings": [], "critical": []}`.
- Existing `test_score_device_missing_data` is corrected to assert score 100 and no warnings.
- Existing `test_score_device_multiple_issues` is updated to remove the uptime-unknown deduction/warning from its expected total and warning count.
- Output shape (`score`, `warnings`, `critical`) is unchanged.

CONSTRAINTS:
- No new dependencies.
- Pure function: no SSH, no CLI wiring, no I/O.
- Do not modify `app/normalization.py` or its output shape.
- Do not add a new "unknown uptime" concept beyond removing the deduction (no new fields/severity levels).

KNOWN RISKS:
- Removing the uptime deduction means devices with genuinely stale/unreachable uptime data are indistinguishable from healthy devices on that axis; acceptable for PoC.

OUTSTANDING RISKS:
- Fixed 80% CPU/memory thresholds may not suit all device roles (carried from PHASE-013).
- CLI integration of `build_device_summary()` and `score_device_health()` remains deferred (carried from PHASE-012/012A/013).
- Cisco format drift and unsupported-vendor defaults remain accepted PoC risks (carried from PHASE-012).

OPEN QUESTIONS:
- None.
