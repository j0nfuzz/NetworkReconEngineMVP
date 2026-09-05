PHASE: PHASE-063A-TargetInputPreflightValidationTestRemediation

STATUS: Implemented

FILES MODIFIED:
- tests/test_cli.py
  - Strengthened test_invalid_target_fails_before_ssh_probe and test_empty_target_fails_before_ssh_probe to monkeypatch both probe_devices and execute_device_collection to raise AssertionError if called.
  - Both tests now prove malformed and empty targets return exit code 1 and emit the expected validation message without ever reaching the SSH/probe boundary.

TESTS ADDED/EXTENDED:
- tests/test_cli.py::test_invalid_target_fails_before_ssh_probe (extended)
- tests/test_cli.py::test_empty_target_fails_before_ssh_probe (extended)

DDR UPDATES:
UNCHANGED DD:2026-09-04 (DD-015)

RISKS INTRODUCED:
- None (test-only change).

RISKS RESOLVED:
- Terra's review finding closed: PHASE-063 acceptance criterion "fail before SSH activity" is now asserted, not merely implied.

OPEN ISSUES:
- None.
