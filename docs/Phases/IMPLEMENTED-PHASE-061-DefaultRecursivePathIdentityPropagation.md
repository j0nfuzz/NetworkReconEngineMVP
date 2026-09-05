PHASE:
PHASE-061-DefaultRecursivePathIdentityPropagation

STATUS:
Implemented

FILES MODIFIED:
- app/orchestrator.py
- tests/test_orchestrator.py
- docs/Phases/PHASE-061-DefaultRecursivePathIdentityPropagation.md
- docs/Phases/IMPLEMENTED-PHASE-061-DefaultRecursivePathIdentityPropagation.md

CHANGES:
- Added _probe_identity() helper in app/orchestrator.py that uses DeviceSSHClient to run "show version" and identify_device() for vendor/platform detection.
- Applied PHASE-055A confidence-gating: probe result overwrites device.vendor and metadata["identity"] only when probe confidence is strictly greater than existing identity confidence.
- run_recursive_collection() now probes devices whose vendor is "auto" or "unknown" before calling execute_device_collection().
- Added regression tests covering auto-vendor resolution, preservation of higher-confidence existing identity, and graceful fallback when probing fails.

VALIDATION:
- `python -m py_compile app/orchestrator.py tests/test_orchestrator.py` passed.
- `pytest tests/test_orchestrator.py -v` passed (15 tests).
- `pytest` full suite passed (295 tests, 1 pre-existing warning).

DDR UPDATES:
UNCHANGED DD:DD-015

RISKS INTRODUCED:
- One extra SSH connection per auto/unknown device on the recursive path.

RISKS RESOLVED:
- Default recursive-path collections no longer silently fall back to the generic profile for vendor="auto" devices, including the PHASE-061A edge case where a higher-confidence identity was retained but device.vendor stayed "auto".

OPEN ISSUES:
- The separate "unreachable" field symptom is not addressed by this phase.
