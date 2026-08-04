PHASE:
Role Detection Remediation (PoC)

STATUS:
Implemented

FILES MODIFIED:
- app/cli.py
- tests/test_cli.py

TESTS ADDED:
- tests/test_cli.py::test_configured_vendor_device_gets_role_classified

DDR UPDATES:
- UNCHANGED DD:2026-08-04

RISKS INTRODUCED:
- None.

RISKS RESOLVED:
- Configured-vendor devices no longer bypass role classification.
- summary.json role field now populated for configured-vendor paths.

OPEN ISSUES:
- Hostname/model heuristics and confidence scoring remain unvalidated against real devices (carried from PHASE-002).
