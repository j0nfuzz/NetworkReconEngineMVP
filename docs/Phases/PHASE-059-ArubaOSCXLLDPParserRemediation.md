PHASE:
ArubaOSCXLLDPParserRemediation

FILES:
app/discovery.py
tests/test_discovery.py

ACCEPTANCE CRITERIA:
- Recognize ArubaOS-CX LLDP field labels `Neighbor System-Name`, `Neighbor Chassis-ID`, and `Neighbor Management-Address` alongside generic labels.
- Return non-empty neighbors from sanitised PHASE-058 LLDP detail evidence.
- Preserve generic LLDP and CDP parsing behavior.

CONSTRAINTS:
- No collector, vendor-profile, orchestrator, traversal, health, or topology changes.
- No summary-form LLDP or CDP enhancements.

KNOWN RISKS:
- ArubaOS-CX record boundaries must match field evidence.

OUTSTANDING RISKS:
- Summary-form LLDP and ArubaOS-CX CDP remain unverified.

OPEN QUESTIONS:
- None.
