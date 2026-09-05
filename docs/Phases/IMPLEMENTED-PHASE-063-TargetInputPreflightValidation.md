PHASE: PHASE-063-TargetInputPreflightValidation

STATUS: Implemented

FILES MODIFIED:
- app/cli.py
  - Added _is_valid_target() helper validating IPv4, IPv6, and DNS hostname syntax without DNS lookups.
  - Added pre-flight validation in main() after device loading and before any SSH probe/collection activity.
- tests/test_cli.py
  - Added parametrized test_is_valid_target covering IPv4, IPv6, hostnames, and malformed inputs.
  - Added test_invalid_target_fails_before_ssh_probe proving "192.168.241" fails fast with a clear message.
  - Added test_empty_target_fails_before_ssh_probe.
  - Added test_valid_target_proceeds_to_collection and test_valid_hostname_proceeds_to_collection proving valid targets are unaffected.

TESTS ADDED:
- tests/test_cli.py::test_is_valid_target
- tests/test_cli.py::test_invalid_target_fails_before_ssh_probe
- tests/test_cli.py::test_empty_target_fails_before_ssh_probe
- tests/test_cli.py::test_valid_target_proceeds_to_collection
- tests/test_cli.py::test_valid_hostname_proceeds_to_collection

DDR UPDATES:
UNCHANGED DD:2026-09-04 (DD-015)

RISKS INTRODUCED:
- Overly strict hostname regex could theoretically reject unusual but valid hostnames; mitigated by permissive RFC-1123-style label matching and IPv6 socket fallback.

RISKS RESOLVED:
- Prevents malformed operator input (e.g. truncated IPv4) from reaching the SSH/DNS layer, eliminating the diagnostic latency class that required PHASE-062.

OPEN ISSUES:
- None.
