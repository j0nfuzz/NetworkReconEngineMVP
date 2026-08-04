PHASE: PHASE-002-RoleDetection

STATUS:
Implemented

FILES MODIFIED:
- app/models.py
  - Added DeviceRole{role, confidence} dataclass.
- app/detector.py
  - Added classify_role(identity, device_name) using hostname/model heuristics.
- app/cli.py
  - Stores detected role in device.metadata["role"].
- app/collector.py
  - summary.json now always includes role and role_confidence.
- docs/DESIGN-DECISION-REGISTER.md
  - Added proposed DD-002 for heuristic-only role classification.

TESTS ADDED:
- tests/test_detector.py
  - classify_role() switch from hostname
  - classify_role() router from hostname
  - classify_role() firewall from hostname
  - classify_role() unknown fallback
  - classify_role() switch from model

DDR UPDATES:
- DD-002 Proposed: Role classification uses deterministic hostname/model heuristics only; defer routing-table/LLDP-based inference.

RISKS INTRODUCED:
- None.

RISKS RESOLVED:
- Missing role classification capability.
- Missing role field in summary.json.

OPEN ISSUES:
- Role confidence scoring remains unvalidated against real devices.
- Heuristic rules may misclassify atypical hostnames/models.
- Routing/LLDP-based role refinement deferred to future phase.
