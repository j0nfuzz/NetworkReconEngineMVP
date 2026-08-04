PHASE:
Credential Management

FILES:
- app/config.py
- tests/test_cli.py

ACCEPTANCE CRITERIA:
- load_devices() supports an optional top-level `default` credentials block (username/password/enable_password) in the YAML config
- Each device entry may omit username/password/enable_password and inherit them from `default`
- A device entry providing its own username/password/enable_password overrides the default for those fields only
- Devices with neither a default nor a per-device value keep existing behaviour (empty string / None), unchanged from today
- Existing config files without a `default` block continue to load unchanged (backward compatible)
- Tests cover: default applied when device omits credentials, per-device override wins over default, no default block present, partial override (e.g. device overrides password only, inherits username)

CONSTRAINTS:
- No new dependencies (reuse existing PyYAML/yaml usage)
- No credential storage/encryption/vault (explicitly deferred per Wishlist)
- No SSH connection changes, no changes to Device dataclass fields
- No changes to app/cli.py or app/collector.py call sites
- Minimal, additive change to load_devices() merging logic only

KNOWN RISKS:
- None beyond those already carried

OUTSTANDING RISKS:
- Plaintext credentials in YAML remain unencrypted (carried forward; encrypted/vault support explicitly deferred to a future phase per Wishlist Phase 8)

OPEN QUESTIONS:
- None.
