PHASE:
EnvironmentCredentialSubstitution

STATUS:
Implemented

FILES MODIFIED:
- app/config.py
  - Added _resolve_credential_value() to resolve exact `${ENV_VAR}` references.
  - Added _resolve_credentials() helper applied to default and per-device credential fields.
  - load_default_credentials() and load_devices() now resolve credential placeholders before merging defaults into devices.
  - Literal credential values continue to work unchanged.
  - Missing environment variables raise ValueError with a message that does not expose secret values.
- tests/test_config_env_substitution.py
  - Added tests for successful substitution, missing variable, mixed literal/substituted values, inheritance, and backward compatibility.
- config/devices.yml.example
  - Added a comment showing the `${ENV_VAR}` syntax for credentials.
- README.md
  - Added environment-variable credential example and error behaviour note.
- docs/DESIGN-DECISION-REGISTER.md
  - Updated DD-010 status from Proposed to Approved.

TESTS ADDED:
- tests/test_config_env_substitution.py (7 tests)

DDR UPDATES:
DD-010 Approved

RISKS INTRODUCED:
- Environment variables can be inspected by privileged local processes.
- Operators must ensure referenced variables are set before collection.

RISKS RESOLVED:
- Credentials no longer need to be stored as plaintext in local YAML files.
- PHASE-041 example templates can now point to environment variables instead of placeholders.

OPEN ISSUES:
- Secure vault/keyring integration remains future work (Wishlist Phase 8 future item).
- DD-007 remains inconclusively validated on real hardware.
