PHASE:
PHASE-008-CredentialManagement

STATUS:
Implemented

FILES MODIFIED:
- app/config.py
- tests/test_config.py (new)

TESTS ADDED:
- test_device_fully_inherits_default_credentials
- test_device_partial_override
- test_device_full_override
- test_legacy_config_without_default

DDR UPDATES:
UNCHANGED DD:2026-08-04

RISKS INTRODUCED:
- None. Merge logic is additive and only populates missing credential fields from an optional default block.

RISKS RESOLVED:
- None.

OPEN ISSUES:
- None.
