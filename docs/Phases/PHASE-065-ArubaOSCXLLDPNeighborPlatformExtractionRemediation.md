PHASE:
PHASE-065-ArubaOSCXLLDPNeighborPlatformExtractionRemediation

OBJECTIVE:
Extend the LLDP neighbor extractor to capture vendor-identifying platform/description text so classify_neighbor_support() can correctly classify real vendor neighbors discovered via ArubaOS-CX LLDP output, unblocking recursive collection expansion.

FILES:
- app/discovery.py
- tests/test_discovery.py

ACCEPTANCE CRITERIA:
- _parse_lldp_neighbors() captures "Neighbor System-Description" into the neighbor record's "platform" field when present, in addition to the existing chassis-ID fallback.
- Existing "platform" fallback-to-chassis-ID behaviour is preserved when no System-Description is available.
- classify_neighbor_support() correctly classifies a neighbor whose System-Description contains a supported vendor marker (e.g. "Aruba R8N85A") as that vendor, using only the extracted record (no source-file changes to app/classification.py required).
- Regression tests added to tests/test_discovery.py using sanitised LLDP fixture text (based on field evidence FT060920260035.zip, pattern only, no real hostnames/IPs) proving System-Description is captured and a real device (e.g. an access point or switch entry) is classifiable.
- No changes to CDP parsing, SSH, orchestrator traversal logic, or recursion algorithm.
- Full test suite passes.

CONSTRAINTS:
- Change confined to the LLDP neighbor-record extraction path in app/discovery.py.
- No changes to app/orchestrator.py, app/classification.py, app/collector.py, or CLI.
- No changes to which vendors are considered "supported" (SUPPORTED_VENDOR_MARKERS unchanged).
- Sanitise all test fixtures per field_tests/FIELDTEST.md; no real hostnames/IPs/serials from FT060920260035.zip may appear in source, tests, or docs.

KNOWN RISKS:
- Some legacy/non-standard device LLDP output may format System-Description differently; extraction should remain best-effort (missing field falls back to existing behaviour).

OUTSTANDING RISKS:
- Devices with a supported vendor marker in System-Description that are not actually SSH-collectible (e.g. access points without CLI shell) will now attempt collection and fail; existing failed/unsupported handling in run_recursive_collection() already covers this, but should be re-validated in a follow-up field run.

OPEN QUESTIONS:
- None.
