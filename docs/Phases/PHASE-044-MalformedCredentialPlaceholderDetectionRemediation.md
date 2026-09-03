PHASE:
MalformedCredentialPlaceholderDetectionRemediation

FILES:
app/config.py
tests/test_config_env_substitution.py
docs/DESIGN-DECISION-REGISTER.md

ACCEPTANCE CRITERIA:
- Any credential field value containing both `${` and `}` anywhere in the string, that does not match the exact `${VALID_ENV_VAR_NAME}` syntax for the entire value, must raise a clear ValueError, not be treated as a literal. This includes values with leading or trailing text around the markers (e.g. `prefix${NRE-BAD}`, `${NRE_USER}suffix`).
- Exact `${ENV_VAR}` references (the entire value matches `^\$\{[A-Za-z_][A-Za-z0-9_]*\}$`) continue to resolve as implemented in PHASE-042/043.
- Values containing no `${` or no `}` marker at all continue to be treated as literal credentials, unchanged (e.g. a value starting with `${` but never closed, such as `${literal prefix`, remains literal since it has no matching `}`).
- Error messages must not expose secret values (only the field name).
- Add regression tests for malformed placeholders embedded with leading/trailing text, in both default and per-device credential fields.
- Full suite passes.

CONSTRAINTS:
- Do not add third-party dependencies.
- Do not modify timeout, recovery, SSH negotiation, vendor detection, collector, or provenance behaviour.
- Do not change the resolution order established in PHASE-042 (resolve before default/device merge).
- Do not alter literal-credential behaviour for values containing no `${` or no `}` marker.

KNOWN RISKS:
- Broadening malformed detection to "contains `${` and `}` anywhere" could reject legitimate literal passwords that happen to contain both characters; this is accepted per the explicit PHASE-042/043 wording and must be documented in README/example templates.

OUTSTANDING RISKS:
- DD-007 remains inconclusively validated on real hardware; timeout investigation remains parked.

OPEN QUESTIONS:
- None.
