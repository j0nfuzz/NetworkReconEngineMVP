PHASE:
CLI Recursive Collection Integration

FILES:
- app/cli.py
- tests/test_cli.py

ACCEPTANCE CRITERIA:
- New CLI flag (e.g. `--recursive`) invokes run_recursive_collection() starting from the first configured device as seed, instead of (or alongside) the existing flat per-device loop.
- Existing default (non-recursive) CLI behavior is completely unchanged when `--recursive` is not passed.
- New CLI flag (e.g. `--checkpoint-file <path>`) enables save_checkpoint() via the on_collected callback during recursive runs.
- If `--checkpoint-file` points to an existing file at startup, load_checkpoint() is used to populate resume_state before calling run_recursive_collection().
- default_credentials passed to run_recursive_collection() are sourced from the already-loaded config's `default` block (reusing load_devices()' existing merge, or reading the raw default block — implementer's choice, document in IMPLEMENTED file).
- Recursive run results (successful/failed/unsupported/bundles) are written using the existing write_bundle() and bundle_manifest.json conventions, unchanged in format.
- Tests cover: recursive flag invokes run_recursive_collection with the seed device, checkpoint file is created when checkpoint flag is set, existing checkpoint is loaded and passed as resume_state, and default (non-recursive) behavior is unaffected.

CONSTRAINTS:
- No new dependencies.
- No concurrency changes.
- No changes to run_recursive_collection(), save_checkpoint(), or load_checkpoint() signatures — cli.py composes existing functions only.
- No Device dataclass changes.
- No changes to existing non-recursive code path behavior or output format.

KNOWN RISKS:
- None beyond those already carried.

OUTSTANDING RISKS:
- Recursive mode currently only supports a single seed device (the first configured entry); multi-seed recursive runs are out of scope for this phase.
- Plaintext checkpoint/credential handling remains an accepted PoC limitation carried from PHASE-008/010.

OPEN QUESTIONS:
- None.
