PHASE:
PHASE-011-CLIRecursiveCollectionIntegration

STATUS:
Implemented

FILES MODIFIED:
- app/cli.py
  - Added `--recursive` and `--checkpoint-file` arguments to `parse_args()`.
  - Imported `run_recursive_collection` from `app.orchestrator`.
  - Imported `save_checkpoint` and `load_checkpoint` from `app.checkpoint`.
  - Added `_run_recursive_cli()` helper to compose the seed device, inferred default credentials, optional resume state, and checkpoint callback.
  - In `main()`, when `--recursive` is passed, call `_run_recursive_cli()` for the first configured device and then write `bundle_manifest.json`/`topology.json` as usual.
  - Non-recursive path remains identical.

- tests/test_cli.py
  - Added `test_parse_args_supports_recursive_and_checkpoint_file`.
  - Added `test_recursive_cli_invokes_orchestrator`.
  - Added `test_recursive_cli_creates_checkpoint_file`.
  - Added `test_recursive_cli_resumes_from_existing_checkpoint`.
  - Added `test_recursive_cli_writes_bundle_manifest`.
  - Added `test_non_recursive_path_unchanged`.
  - Added `test_missing_checkpoint_file_is_handled`.

TESTS ADDED:
- tests/test_cli.py::test_parse_args_supports_recursive_and_checkpoint_file
- tests/test_cli.py::test_recursive_cli_invokes_orchestrator
- tests/test_cli.py::test_recursive_cli_creates_checkpoint_file
- tests/test_cli.py::test_recursive_cli_resumes_from_existing_checkpoint
- tests/test_cli.py::test_recursive_cli_writes_bundle_manifest
- tests/test_cli.py::test_non_recursive_path_unchanged
- tests/test_cli.py::test_missing_checkpoint_file_is_handled

DDR UPDATES:
UNCHANGED DD:2026-08-04

RISKS INTRODUCED:
- Recursive mode uses only the first configured device as seed; multi-seed recursion remains out of scope.
- Default credentials are inferred from the seed device fields after `load_devices()` merge; this matches current config behaviour but is an implementation choice because the raw `default` block is not exposed by `load_devices()`.
- Plaintext checkpoint/credential persistence remains a PoC limitation carried from PHASE-008/010.

RISKS RESOLVED:
- Recursive collection and checkpoint resume were unreachable from the CLI; they are now wired into the entry point.

OPEN ISSUES:
- None.
