PHASE:
MalformedCredentialPlaceholderValidation

STATUS:
Implemented

FILES MODIFIED:
- app/config.py
  - Added _ENV_MALFORMED_RE to detect strings containing `${...}` that are not valid env-var references.
  - Updated _resolve_credential_value() to reject malformed `${...}` references with a clear ValueError before resolving valid references.
  - Error messages include the credential field name but do not expose the raw credential value.
  - Valid `${ENV_VAR}` references continue to resolve unchanged.
  - Missing-variable handling remains unchanged.
  - Literal values without `${`/`}` markers remain unchanged.
  - _resolve_credentials() now passes the field name to _resolve_credential_value() for clearer diagnostics.
- tests/test_config_env_substitution.py
  - Added regression tests for malformed placeholders with illegal characters, empty placeholders, malformed placeholder with spaces, malformed placeholder in per-device fields, and a literal value that starts with `${` but is not a closed reference.
- docs/DESIGN-DECISION-REGISTER.md
  - Re-proposed DD-010 (environment credential substitution) now that malformed placeholders are rejected.

TESTS ADDED:
- tests/test_config_env_substitution.py (5 new tests, 12 total)

DDR UPDATES:
DD-010 Re-proposed (pending GPT Reviewer approval)

VALIDATION RESULTS:
- Targeted tests: 12 passed
- Full primary test suite: 196 passed

RISKS INTRODUCED:
- None (narrow remediation of existing defect).

RISKS RESOLVED:
- Malformed `${...}` credential references are no longer silently accepted as literal credentials.
- PHASE-042 acceptance criterion for rejecting malformed references is now satisfied.

OPEN ISSUES:
- DD-007 remains inconclusively validated on real hardware.
- DD-010 requires GPT reviewer approval to become authoritative.
