PHASE:
ArubaOSCXLLDPParserRemediation

STATUS:
Implemented

FILES MODIFIED:
- app/discovery.py
  - Updated _parse_lldp_neighbors() to recognize ArubaOS-CX LLDP field labels (Neighbor System-Name, Neighbor Chassis-ID, Neighbor Management-Address) alongside existing generic labels (System Name:, Chassis id:).
  - Added chassis-id-based block splitting for ArubaOS-CX while preserving existing Chassis id: delimiter.
  - Added identity fallback: Neighbor System-Name → Neighbor Management-Address → IPv4 chassis-id → raw chassis-id.
  - Added IP fallback from Neighbor Management-Address when chassis-id is not an IPv4 address.
- tests/test_discovery.py
  - New regression tests for ArubaOS-CX LLDP detail parsing using the sanitised PHASE-058 field evidence.
  - Existing generic LLDP label parsing regression coverage.

TESTS ADDED:
- test_extract_neighbors_arubacx_lldp_detail_finds_neighbors
- test_extract_neighbors_arubacx_lldp_detail_uses_chassis_id_when_no_system_name
- test_extract_neighbors_arubacx_lldp_detail_uses_management_address_fallback
- test_extract_neighbors_generic_lldp_labels_still_parsed

DDR UPDATES:
UNCHANGED DD:DD-007

RISKS INTRODUCED:
- Regex/line-based parser changes for LLDP could theoretically affect other vendors if field labels overlap; mitigated by additive matching and existing regression tests.
- Only one ArubaOS-CX evidence bundle exists; unseen edge cases remain unverified.

RISKS RESOLVED:
- ArubaOS-CX neighbor discovery is now functional for `show lldp neighbor-info detail` output.

OPEN ISSUES:
- `show lldp neighbor-info` (summary form) parsing is not implemented.
- Legacy CDP parsing on ArubaOS-CX is not addressed.
