PHASE: PHASE-062-RecursiveCollectionProbeDiagnosticVisibility

STATUS: Defined

OBJECTIVE:
Surface the existing SSH probe error string through recursive --verbose output when identity detection is skipped because the device is unreachable, preventing multi-hour root-cause investigations that currently require post-hoc bundle analysis.

ACCEPTANCE CRITERIA:
- Recursive verbose output displays the probe error when identity detection is skipped because the probe is unreachable.
- Existing PHASE-061/061A identity-detection and confidence-gating behaviour remains unchanged.
- Existing collection behaviour, traversal behaviour, and command execution flow remain unchanged.
- Regression coverage added in tests/test_orchestrator.py and tests/test_cli.py.
- py_compile passes.
- Full pytest suite passes.

CONSTRAINTS:
- Do not modify probe(), connect(), retry, timeout, KEX, auth or SSH logic.
- Do not alter command execution flow.
- Preserve all current collection, confidence-gating and identity-detection behaviour.

FILES:
- app/orchestrator.py
- app/cli.py
- tests/test_orchestrator.py
- tests/test_cli.py

IMPLEMENTATION NOTES:
- _probe_identity() currently returns None and discards the probe error when probe.get("reachable") is False.
- Change _probe_identity() to return Optional[str]: the probe error when unreachable, None otherwise.
- run_recursive_collection() accumulates these errors into a "probe_errors" dict keyed by device name and returns it in its result dict.
- _run_recursive_cli() logs each probe_error entry via log_verbose() before logging the final collection status.
- Add regression tests proving the error is returned by the orchestrator and visible in verbose CLI output.
