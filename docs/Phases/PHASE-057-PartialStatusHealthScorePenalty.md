PHASE:
PartialStatusHealthScorePenalty

FILES:
app/health.py
tests/test_health.py

ACCEPTANCE CRITERIA:
- `score_device_health()` reduces score and adds a warning when `summary["status"] == "partial"` or `summary.get("failed_commands")` is non-empty.
- A bundle with zero failed commands and `status == "collected"` continues to score 100 with no warnings (no behaviour change for the passing case).
- A regression test asserts a partial-status/failed-commands summary no longer scores 100 with an empty warnings list.

CONSTRAINTS:
- Do not change the existing CPU/memory/interface-error thresholds or scoring weights.
- Deterministic; no new dependencies.

KNOWN RISKS:
- The exact penalty weight for failed commands is a judgement call and may need tuning once cross-vendor field evidence exists.

OUTSTANDING RISKS:
- None.

OPEN QUESTIONS:
- Exact penalty weight is not architecturally mandated; implementer should choose a value consistent with the existing 10-15 point deductions, subject to reviewer confirmation.
