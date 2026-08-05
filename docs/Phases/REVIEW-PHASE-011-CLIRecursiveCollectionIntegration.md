REVIEW PHASE:
PHASE-011-CLIRecursiveCollectionIntegration

REVIEW VERDICT:
Not Approved

1. Critical Issues
None.

2. Major Issues
- Issue: `--recursive --dry-run` calls `run_recursive_collection()`, which always invokes `execute_device_collection(device)` without `dry_run=True`.
	Why It Matters: The CLI advertises dry-run validation, but recursive mode can make real SSH connections and collection calls.
	Recommended Fix: Add a minimal, backwards-compatible dry-run path before enabling approval; do not redesign orchestration.

- Issue: Recursive default credentials are copied from the first seed device, not sourced from the config `default` block.
	Why It Matters: Seed-specific credential overrides are incorrectly inherited by discovered neighbors, violating the phase criterion.
	Recommended Fix: Read the existing config `default` block in CLI and pass only its credential fields to `run_recursive_collection()`.

3. DDR Review
UNCHANGED DD:2026-08-04. No architectural decision is required.

4. Outstanding Risks
- Single seed and plaintext checkpoints remain accepted PoC limitations.

5. Open Questions
None.

6. Recommended Next Phase
PHASE-011A remediation for the two issues above; defer parallel collection.
