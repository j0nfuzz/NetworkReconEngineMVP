PHASE:
ArubaOSCXLLDPRecordBoundaryRemediation

FILES:
app/discovery.py
tests/test_discovery.py

ACCEPTANCE CRITERIA:
- ArubaOS-CX LLDP detail records are split on the evidenced `Port :` boundary.
- Each emitted ArubaOS-CX neighbor reads `Neighbor System-Name`, `Neighbor Chassis-ID`, and `Neighbor Management-Address` from one Port-bounded record.
- Header and non-record blocks are skipped.
- Existing generic `Chassis id:`/`System Name:` LLDP and CDP parsing remain unchanged and passing.
- Regression assertions prove same-record association using sanitised PHASE-058 evidence.

CONSTRAINTS:
- Only listed files may change.
- No collector, vendor-profile, orchestrator, traversal, health, topology, summary-form LLDP, or CDP changes.

KNOWN RISKS:
- One ArubaOS-CX detail output shape is evidenced; unseen formats remain unverified.

OUTSTANDING RISKS:
- Summary-form LLDP and ArubaOS-CX CDP remain unverified.

OPEN QUESTIONS:
- None.
