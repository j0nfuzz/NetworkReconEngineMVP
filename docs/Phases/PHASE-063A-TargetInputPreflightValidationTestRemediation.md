PHASE: PHASE-063A-TargetInputPreflightValidationTestRemediation

STATUS: Defined

OBJECTIVE:
Strengthen PHASE-063 regression tests so they explicitly prove that malformed and empty target inputs fail before any SSH/probe activity, addressing Terra's review finding.

ACCEPTANCE CRITERIA:
- test_invalid_target_fails_before_ssh_probe and test_empty_target_fails_before_ssh_probe patch a probe/SSH boundary to raise if invoked.
- Both tests assert the patched boundary is never reached while still returning exit code 1 and emitting the expected validation error.
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
