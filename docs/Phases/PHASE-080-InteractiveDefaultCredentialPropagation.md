PHASE:
PHASE-080-InteractiveDefaultCredentialPropagation

FILES:
- app/cli.py
- README.md
- tests/test_cli.py

ACCEPTANCE CRITERIA:
- `_prompt_interactive_inventory()` writes a `default:` block containing the prompted username and password alongside the existing single-device `devices:` block.
- `load_default_credentials()` on the generated runtime YAML returns the prompted credentials, so `run_recursive_collection`/`run_parallel_scoped_collection` construct discovered-neighbour devices with real credentials (existing orchestrator behaviour consumes them unchanged).
- Interactive seed-device behaviour is unchanged: same prompts, same devices block, same temp-file lifecycle and cleanup (PHASE-022 guarantees preserved).
- Regression test proves the generated runtime YAML yields default credentials equal to the mocked prompt inputs.
- Regression test proves an orchestrator-constructed neighbour device receives the default credentials when the default block is present.
- README documents that interactive-prompted credentials are reused as default credentials for discovered neighbours, and that config-file users should set a `default:` block for recursive runs.
- Full existing suite passes.

CONSTRAINTS:
- No changes to app/config.py credential resolution, env-substitution, or malformed-placeholder validation (DD-010 surface untouched).
- No changes to orchestrator traversal, queueing, classification, or checkpoint logic.
- No interactive mid-run credential prompting (MVP candidate B explicitly rejected by the Architect; the default block is the MVP candidate A/C mechanism).
- Prompted literal credentials containing both `${` and `}` remain subject to the existing DD-010 rejection trade-off; no new handling.

KNOWN RISKS:
- Discovered neighbours now receive real credentials; a wrong-but-valid credential set can produce auth-failure log entries on devices outside the intended scope (identical to existing behaviour for config-file users who set default credentials; bounded by max_devices and scope rules).
- Non-interactive/TTY-limited automation is unaffected (uses --config flows).

OUTSTANDING RISKS:
- Credential rotation/git-history thread (PHASE-041) remains open; unrelated to this phase.

OPEN QUESTIONS:
- None.
