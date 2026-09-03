PHASE:
EnvironmentCredentialSubstitution

FILES:
app/config.py
tests/test_config.py
config/devices.yml.example
config/interactive_devices.yml.example
README.md
docs/DESIGN-DECISION-REGISTER.md

ACCEPTANCE CRITERIA:
- Support exact `${ENV_VAR}` references for username, password, and enable_password in default and per-device config fields.
- Resolve variables before existing default/device credential merging; explicit per-device values still override defaults.
- Reject missing or malformed credential variable references with a clear error that does not expose secret values.
- Preserve literal credential values and existing config behaviour.
- Update templates and README to use and document environment references without committing secret values.
- Add focused parsing/precedence/error tests; full suite passes.

CONSTRAINTS:
- Do not add third-party dependencies, persistent secret stores, or vault/keyring integrations.
- Do not modify timeout, recovery, SSH negotiation, vendor detection, collector, or provenance behaviour.
- Do not read, log, serialize, or expose resolved secrets outside current connection use.

KNOWN RISKS:
- Environment variables can be visible to privileged local processes; a secure vault remains future work.
- Operators must provide the referenced variables before collection.

OUTSTANDING RISKS:
- DD-007 remains inconclusively validated on real hardware; timeout investigation is parked until reachable hardware is available.
- The original device-side timeout cause remains unknown.

OPEN QUESTIONS:
- Should a future credential provider support Windows Credential Manager or an enterprise vault?