PHASE:
MalformedCredentialPlaceholderDetectionRemediation

STATUS:
Implemented

FILES MODIFIED:
- app/config.py
  - Replaced the `startswith("${")` guard and separate malformed regex with a single exact-match check followed by a containment check.
  - `_ENV_PLACEHOLDER_RE` continues to match valid exact `${ENV_VAR}` references.
  - `_ENV_MARKERS_RE` detects any credential value containing both `${` and `}` anywhere in the string.
  - `_resolve_credential_value()` now resolves exact valid references first, then rejects any remaining value containing both markers, and finally returns literal values unchanged.
  - Missing-variable handling remains unchanged.
  - Error messages include the credential field name and do not expose the raw value.
- tests/test_config_env_substitution.py
  - Added regression tests for embedded malformed placeholders with leading text, trailing text, leading and trailing text, and a literal value that contains `}` but no `${`.
- docs/DESIGN-DECISION-REGISTER.md
  - Re-proposed DD-010 (environment credential substitution) now that any value containing malformed `${...}` syntax is rejected regardless of position.

TESTS ADDED:
- tests/test_config_env_substitution.py (4 new tests, 16 total)

DDR UPDATES:
DD-010 Re-proposed (pending GPT Reviewer approval)

VALIDATION RESULTS:
- Targeted tests: 16 passed
- Full primary test suite: 200 passed

RISKS INTRODUCED:
- None (narrow remediation of existing defect).

RISKS RESOLVED:
- Embedded malformed `${...}` credential references are no longer silently accepted as literal credentials.
- PHASE-043 acceptance criterion for rejecting malformed references is now satisfied.

OPEN ISSUES:
- DD-007 remains inconclusively validated on real hardware.
- DD-010 requires GPT reviewer approval to become authoritative.
