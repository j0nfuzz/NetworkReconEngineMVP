PHASE:
CLI Recursive Collection Remediation

FILES:
- app/cli.py
- tests/test_cli.py

ACCEPTANCE CRITERIA:
- `--recursive --dry-run` no longer performs real SSH/collection actions. `_run_recursive_cli()` must honor `dry_run` when composing recursive collection, without changing `run_recursive_collection()`'s signature.
- Default credentials passed to `run_recursive_collection()` are sourced from the raw config `default` block read directly from the YAML payload (not from the merged seed device), so seed-specific credential overrides are not leaked to discovered neighbors.
- Existing non-recursive behavior, bundle output, and manifest output remain unchanged.
- Tests cover: recursive `--dry-run` does not invoke real collection side effects, and default_credentials passed to `run_recursive_collection()` match the raw config default block even when the seed device has overridden credentials.

CONSTRAINTS:
- No new dependencies.
- No changes to `run_recursive_collection()`, `save_checkpoint()`, or `load_checkpoint()` signatures.
- No Device dataclass changes.
- No concurrency or multi-seed changes.

KNOWN RISKS:
- `run_recursive_collection()` has no `dry_run` parameter; if it cannot be threaded through without a signature change, the smallest compliant fix is to read the config `default` block directly in `app/config.py` (e.g. a small helper) or `app/cli.py`, and to gate recursive dry-run at the CLI boundary (e.g. skip invoking `run_recursive_collection()` and report a validation-only summary, consistent with how `--dry-run` is documented).

OUTSTANDING RISKS:
- Single-seed limitation remains out of scope (carried from PHASE-011).
- Plaintext checkpoint/credential handling remains an accepted PoC limitation.

OPEN QUESTIONS:
- None.
