PHASE:
PHASE-059A-ArubaOSCXLLDPRecordBoundaryRemediation

STATUS:
Implemented

FILES MODIFIED:
- app/discovery.py
- tests/test_discovery.py
- docs/Phases/PHASE-059-ArubaOSCXLLDPParserRemediation.md
- docs/Phases/PHASE-059A-ArubaOSCXLLDPRecordBoundaryRemediation.md
- docs/Phases/IMPLEMENTED-PHASE-059A-ArubaOSCXLLDPRecordBoundaryRemediation.md

CHANGES:
- Detect ArubaOS-CX LLDP detail output by its `Neighbor Chassis-ID` field label.
- Split ArubaOS-CX detail output on exact `Port :` records and skip blocks without a chassis ID.
- Extract ArubaOS-CX system name, chassis ID, and management address only from the current Port-bounded block.
- Preserve generic LLDP `Chassis id:` parsing and CDP behavior.
- Strengthen the ArubaOS-CX regression to assert the named neighbor carries its own management IPv4 address, rather than merely asserting neighbor presence.

VALIDATION:
- `python -m py_compile app/discovery.py tests/test_discovery.py` passed.
- `.\\.venv\\Scripts\\python.exe -m pytest tests/test_discovery.py -v` passed: 4 passed.
- `.\\.venv\\Scripts\\python.exe -m pytest tests/test_cli.py -v -k "neighbor or cdp or lldp"` passed: 11 passed, 79 deselected.
- `.\\.venv\\Scripts\\python.exe -m pytest` passed: 289 passed, 1 existing warning.

DDR UPDATES:
UNCHANGED DD:DD-015

RISKS INTRODUCED:
- ArubaOS-CX detail parsing is based on the PHASE-058 observed format only.

RISKS RESOLVED:
- Adjacent ArubaOS-CX LLDP records no longer cross-associate system names, chassis IDs, and management addresses.

OPEN ISSUES:
- Summary-form LLDP and ArubaOS-CX CDP remain unverified and out of scope.
