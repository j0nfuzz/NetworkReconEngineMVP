PHASE:
Role Detection (PoC)

FILES:
- app/models.py
- app/detector.py
- app/cli.py
- app/collector.py
- tests/test_detector.py

ACCEPTANCE CRITERIA:
- DeviceRole{role, confidence} returned by classify_role(identity, device_name)
- Falls back to role="unknown" on no match
- cli.py stores role in device.metadata["role"]
- summary.json gains role field
- Tests cover switch, router, firewall, unknown
- No regressions

CONSTRAINTS:
- No new SSH commands
- Hostname/model heuristics only (no raw-output parsing yet)
- Maintain backwards compatibility

KNOWN RISKS:
- Hostname naming conventions vary by customer
- Model-based inference incomplete for firewalls/APs

OUTSTANDING RISKS:
- Confidence scoring unvalidated (carried from PHASE-001)
- No real device sample corpus (carried from PHASE-001)

OPEN QUESTIONS:
- Should routing-table/LLDP-based role refinement be a separate phase?

---

## Review History

### Review 1

Date: 2026-08-04

Reviewer: GPT

Verdict: Not Approved

Reason:

- Configured-vendor devices bypass classify_role().
- Role remains "unknown" for non-auto vendors.

Required Fixes:

- Apply classify_role() to configured-vendor path.
- Add test coverage for configured-vendor classification.

DDR Impact:

- DD-002 remains Proposed pending fix and review.

---

## Review 2

Date: 2026-08-04

Reviewer: Claude (Architect)

Verdict: Reviewer finding upheld — Rejected

Reason:

- Confirmed classify_role() and identify_device() are only invoked inside the `vendor == "auto"` branch of app/cli.py; configured-vendor devices never receive role classification.
- Acceptance criteria for PHASE-002 do not restrict role classification to auto-detected vendors, so this is an unmet criterion rather than out-of-scope behaviour.

DDR Impact:

- DD-002 remains Proposed; classification design unaffected, integration gap tracked under PHASE-002A.

---

## Implementation Status

Status: Rejected — Remediation Required

Created:
2026-08-04

Implemented:
2026-08-04  

Approved:

Remediation Phase:
PHASE-002A-RoleDetectionRemediation.md

Phase Owner:
Role Detection (PoC)