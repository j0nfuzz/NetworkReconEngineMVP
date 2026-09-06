PHASE:
PHASE-073-RecursiveCollectionPerDeviceProgressLogging

FILES:
app/cli.py
tests/test_cli.py

ACCEPTANCE CRITERIA:
- _run_recursive_cli() logs a "[verbose] Starting device: ..." (or equivalent) line per device before its collection begins, matching the existing sequential-path pattern.
- Existing "[verbose] Finished collection for {name}: ..." lines remain unchanged.
- No change to collection, traversal, checkpoint, or classification behaviour.
- Regression test in tests/test_cli.py proves per-device start logging appears in recursive verbose output.

CONSTRAINTS:
- Do not modify run_recursive_collection(), run_parallel_scoped_collection(), classify_neighbors(), or SSH/probe logic.
- Observability-only change.
- No change to PHASE-062 probe_errors behaviour.

KNOWN RISKS:
- None (logging-only, additive).

OUTSTANDING RISKS:
- None carried forward.

OPEN QUESTIONS:
- None.
