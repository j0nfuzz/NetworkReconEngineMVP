PHASE: PHASE-063-TargetInputPreflightValidation

STATUS: Defined

OBJECTIVE:
Validate target hostname/IP syntax before any SSH activity, failing fast on malformed input such as the truncated IPv4 address observed in the field ("192.168.241"), preventing unnecessary DNS resolution and SSH probe attempts.

ACCEPTANCE CRITERIA:
- Before any SSH probe or collection, each loaded device's hostname is validated for syntactic correctness.
- Valid IPv4 addresses are accepted.
- Valid IPv6 addresses are accepted.
- Valid DNS hostnames are accepted.
- Malformed input (e.g. truncated IPv4, empty string) is rejected with a clear, actionable error message.
- No DNS lookups are performed during validation.
- The validated ArubaOS-CX collection path is unaffected.
- Regression tests added for valid IPv4, valid hostname, malformed IPv4, and empty target.
- py_compile passes.
- Relevant tests pass.

CONSTRAINTS:
- Do not modify probe(), connect(), retry, timeout, KEX, auth, identity detection, collection, traversal, or topology logic.
- Do not alter command execution flow for valid targets.
- Validation must be syntax-only and use only built-in Python modules.

FILES:
- app/cli.py
- tests/test_cli.py
