PHASE: PHASE-063B-TargetInputPreflightValidationRecursiveProbeTestRemediation

STATUS: Defined

OBJECTIVE:
Close the remaining review gap in PHASE-063/063A by ensuring the two fail-fast tests also guard the default recursive collection path through app.cli.run_recursive_collection.

ACCEPTANCE CRITERIA:
- test_invalid_target_fails_before_ssh_probe and test_empty_target_fails_before_ssh_probe additionally monkeypatch app.cli.run_recursive_collection to raise AssertionError if invoked.
- Existing patches for probe_devices and execute_device_collection are retained.
- Both tests still assert exit code 1 and the expected validation error message.
- No production code is changed.
- py_compile passes.
- Relevant tests pass.
- Full pytest suite passes.

CONSTRAINTS:
- tests/test_cli.py only.
- Do not modify app/cli.py.
- Do not alter validation behaviour.
- Do not weaken existing assertions.

FILES:
- tests/test_cli.py
