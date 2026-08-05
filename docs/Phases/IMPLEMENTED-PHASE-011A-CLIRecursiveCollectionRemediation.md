PHASE:
PHASE-011A-CLIRecursiveCollectionRemediation

STATUS:
Implemented

FILES MODIFIED:
- app/cli.py
  - `_run_recursive_cli()` now accepts `dry_run` and `config_path` instead of `devices_data`.
  - Recursive defaults are loaded via `load_default_credentials(config_path)`, reading the raw config `default` block.
  - When `dry_run=True`, recursive mode short-circuits to `execute_device_collection(seed_device, dry_run=True)` and does not invoke `run_recursive_collection()`.
  - Updated `_run_recursive_cli()` call site in `main()` accordingly.
- app/config.py
  - Added `_load_config_payload()` helper to share raw YAML parsing.
  - Added `load_default_credentials()` to expose credential fields from the raw `default` block without seed-device merge side effects.
- tests/test_cli.py
  - Updated existing recursive tests to run in real (non-dry-run) mode and use real config files so `load_default_credentials()` works.
  - Added `test_recursive_cli_dry_run_does_not_invoke_orchestrator`.
  - Added `test_recursive_cli_uses_config_default_block_for_credentials`.
  - Added `test_load_default_credentials_reads_raw_config_block`.
  - Added `test_load_default_credentials_returns_empty_when_no_default`.

TESTS ADDED:
- tests/test_cli.py::test_recursive_cli_dry_run_does_not_invoke_orchestrator
- tests/test_cli.py::test_recursive_cli_uses_config_default_block_for_credentials
- tests/test_cli.py::test_load_default_credentials_reads_raw_config_block
- tests/test_cli.py::test_load_default_credentials_returns_empty_when_no_default

DDR UPDATES:
UNCHANGED DD:2026-08-04

RISKS INTRODUCED:
- None.

RISKS RESOLVED:
- Recursive `--dry-run` no longer performs real collection actions.
- Discovered neighbors no longer inherit seed-device credential overrides; defaults now come from the config `default` block.

OPEN ISSUES:
- None.
