PHASE: PHASE-063B-TargetInputPreflightValidationRecursiveProbeTestRemediation

STATUS: Implemented

IMPLEMENTATION SUMMARY:
Updated tests/test_cli.py to guard the default recursive collection path in the two fail-fast tests:
- test_invalid_target_fails_before_ssh_probe
- test_empty_target_fails_before_ssh_probe

Both tests now monkeypatch app.cli.run_recursive_collection (in addition to the existing probe_devices and execute_device_collection guards) so that reaching the recursive collection boundary raises AssertionError.

No production code was modified.

VALIDATION:
- python -m py_compile tests/test_cli.py: passed
- pytest tests/test_cli.py::test_invalid_target_fails_before_ssh_probe tests/test_cli.py::test_empty_target_fails_before_ssh_probe: 2 passed
- Full pytest suite: 316 passed, 1 warning

FILES CHANGED:
- tests/test_cli.py
