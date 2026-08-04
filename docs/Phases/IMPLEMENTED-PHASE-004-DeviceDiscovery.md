PHASE:
Device Discovery (PoC)

STATUS:
Implemented

FILES MODIFIED:
- app/discovery.py (new)
- app/collector.py
- tests/test_cli.py

TESTS ADDED:
- tests/test_cli.py::test_extract_neighbors_cisco_cdp
- tests/test_cli.py::test_extract_neighbors_returns_empty_when_no_discovery_output
- tests/test_cli.py::test_execute_device_collection_dry_run_has_empty_neighbors

DDR UPDATES:
- UNCHANGED DD:2026-08-04

RISKS INTRODUCED:
- CDP/LLDP parsing is regex-based and may miss neighbors on non-standard formatting.

RISKS RESOLVED:
- Existing collected discovery commands now produce structured neighbor output.

OPEN ISSUES:
- Aruba/Arista/Juniper LLDP parsing is best-effort only; real device samples may require refinement.
