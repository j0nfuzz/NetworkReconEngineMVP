PHASE:
PHASE-072-ArubaOSCXNeighborClassificationMetadataRemediation

FILES:
app/discovery.py
tests/test_discovery.py

ACCEPTANCE CRITERIA:
- ArubaOS-CX LLDP branch of _parse_lldp_neighbors() populates "platform" from Neighbor System-Description when present.
- classify_neighbor_support() correctly classifies the sanitised PHASE-071 Aruba neighbor (HOSTNAME-06) as "aruba".
- Existing ip/neighbor extraction behaviour unchanged; no regression to PHASE-058/067 tests.
- Regression tests use sanitised field-evidence-derived fixtures (System-Description + Capabilities present/absent cases).

CONSTRAINTS:
- No changes to classify_neighbor_support(), traversal, SSH, or CLI logging.
- No changes to CDP parsing.
- Additive field population only.

KNOWN RISKS:
- System-Description free text may vary by vendor; matching remains heuristic, same risk class as existing CDP platform capture.

OUTSTANDING RISKS:
- Console-progress visibility during recursive collection remains unaddressed (separate phase).

OPEN QUESTIONS:
- None.
