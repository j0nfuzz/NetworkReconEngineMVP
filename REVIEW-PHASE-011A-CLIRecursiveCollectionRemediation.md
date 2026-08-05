REVIEW PHASE:
PHASE-011A-CLIRecursiveCollectionRemediation

1. REVIEW VERDICT
Approved.

2. CRITICAL ISSUES
None.

3. MAJOR ISSUES
None.

4. DDR REVIEW
UNCHANGED DD:2026-08-04. The remediation composes existing CLI, configuration, and recursive collection behavior without architectural change.

5. OUTSTANDING RISKS
- Recursive dry-run validates and writes a seed bundle only; it does not discover neighbors. This is the accepted CLI-boundary safeguard required by the phase.
- Single-seed collection and plaintext checkpoints remain accepted PoC limitations.

6. OPEN QUESTIONS
None.

7. RECOMMENDED NEXT PHASE
No remediation follow-up. Re-approve PHASE-011/011A; then consider Parallel Collection.

8. VALIDATION
- `tests/test_cli.py`: 49 passed.
- Full suite: 83 passed.
- Recursive dry-run skips `run_recursive_collection()` and invokes the collector with `dry_run=True`.
- Recursive defaults are read from the raw `default` block; seed overrides do not become neighbor defaults.
- Existing checkpoint/resume, manifest, bundle, and non-recursive paths remain intact.
