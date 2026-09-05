PHASE:
ArubaOSCXLLDPNeighborFormatFieldCapture

FILES:
(none — no source or test files are modified in this phase)
Outputs only: docs/FieldEvidence/PHASE-058-<timestamp>-arubacx-lldp-format.md

ACCEPTANCE CRITERIA:
- Execute `show lldp neighbor-info detail` (and `show lldp neighbor-info` if reachable) against a reachable ArubaOS-CX device using the existing flat collection path.
- Record raw, sanitised output (per field_tests/FIELDTEST.MD policy) in docs/FieldEvidence/PHASE-058-<timestamp>-arubacx-lldp-format.md.
- Document the observed field-name mapping (e.g. `Neighbor System-Name`, `Neighbor Chassis-ID`, `Neighbor Management-Address`) without modifying app/discovery.py.
- If no reachable ArubaOS-CX device is available, record the phase outcome as "blocked — no reachable device" per PHASE-040/046 precedent; this is an acceptable phase conclusion, not a failure.

CONSTRAINTS:
- Data-collection only; no parser, classifier, or discovery.py changes in this phase.
- Read-only commands only; no configuration or state-changing commands.

KNOWN RISKS:
- No reachable ArubaOS-CX device may be available at execution time.

OUTSTANDING RISKS:
- Neighbour discovery remains non-functional on ArubaOS-CX until a follow-on parsing phase consumes this evidence.

OPEN QUESTIONS:
- Whether the same device also emits legacy CDP frames worth capturing alongside LLDP, for completeness of the discovery.py fix scope.
