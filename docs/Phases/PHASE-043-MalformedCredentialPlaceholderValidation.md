PHASE:
MalformedCredentialPlaceholderValidation

FILES:
app/config.py
tests/test_config_env_substitution.py
docs/DESIGN-DECISION-REGISTER.md

ACCEPTANCE CRITERIA:
- Any credential field value that appears to be an environment-variable reference (contains `${` and `}`) but does not match the exact `${VALID_ENV_VAR_NAME}` syntax must raise a clear ValueError, not be treated as a literal.
- Exact `${ENV_VAR}` references continue to resolve as implemented in PHASE-042.
- Values containing no `${`/`}` markers at all continue to be treated as literal credentials, unchanged.
- Error messages must not expose secret values (only the malformed reference text and field name).
- Add regression tests for malformed placeholders in both default and per-device credential fields.
- Full suite passes.

CONSTRAINTS:
- Do not add third-party dependencies.
- Do not modify timeout, recovery, SSH negotiation, vendor detection, collector, or provenance behaviour.
- Do not change the resolution order established in PHASE-042 (resolve before default/device merge).
- Do not alter literal-credential behaviour for values with no `${`/`}` markers.

KNOWN RISKS:
- Overly broad "looks like a reference" detection could reject legitimate literal passwords that happen to contain `${` or `}`; scope detection narrowly to reduce false positives.

OUTSTANDING RISKS:
- DD-007 remains inconclusively validated on real hardware; timeout investigation remains parked.

OPEN QUESTIONS:
- None.
