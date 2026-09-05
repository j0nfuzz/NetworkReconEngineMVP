PHASE: PHASE-062-RecursiveCollectionProbeDiagnosticVisibility

STATUS: Implemented

FILES MODIFIED:
- app/orchestrator.py
  - _probe_identity() now returns Optional[str] probe error when the device is unreachable.
  - run_recursive_collection() collects probe errors into "probe_errors" and returns them in the result dict.
- app/cli.py
  - _run_recursive_cli() logs each probe error via log_verbose() before the final collection-status line.
- tests/test_orchestrator.py
  - Extended test_probe_failure_does_not_block_collection to assert probe_errors is populated.
- tests/test_cli.py
  - Added test_run_recursive_cli_verbose_logs_probe_errors to prove verbose output surfaces the probe error.

TESTS ADDED:
- tests/test_orchestrator.py::test_probe_failure_does_not_block_collection (extended)
- tests/test_cli.py::test_run_recursive_cli_verbose_logs_probe_errors

DDR UPDATES:
UNCHANGED DD:2026-09-04 (DD-015)

RISKS INTRODUCED:
- None. The change is observability-only; no collection, identity or SSH behaviour is altered.

RISKS RESOLVED:
- Eliminates the observability gap that delayed diagnosis of the malformed-target field issue ([Errno 11001] getaddrinfo failed).

OPEN ISSUES:
- None.
