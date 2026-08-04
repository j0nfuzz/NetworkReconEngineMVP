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
