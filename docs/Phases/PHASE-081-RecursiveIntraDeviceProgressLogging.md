PHASE:
PHASE-081-RecursiveIntraDeviceProgressLogging

FILES:
- app/collector.py
- app/orchestrator.py
- app/cli.py
- tests/test_collector.py
- tests/test_orchestrator.py
- tests/test_cli.py

ACCEPTANCE CRITERIA:
- `execute_device_collection()` accepts an optional `progress` callback (default None) and, when provided, emits one line before each meaningful wait point: SSH probe start, probe result, identity probe (when present on the path), connection, and each command as `(i/N) <command>`.
- `run_recursive_collection()` accepts an optional `on_progress` callback (default None), forwards it to `execute_device_collection()`, and emits its own identity-phase line consistent with PHASE-061/061A wiring.
- `app/cli.py` routes the recursive sequential path's progress callback into the existing `log_verbose` mechanism so lines appear on the console and in console.log under verbose capture.
- Zero behaviour change when callbacks are omitted: same returns, same artefacts, same summary fields; quiet (non-verbose) runs emit nothing new.
- Regression tests: collector emits expected per-command progress sequence via callback (mocked SSH); orchestrator forwards the callback; cli wires log_verbose; all three prove no-change when callback is None.
- Full existing suite passes.

CONSTRAINTS:
- Logging only: no changes to traversal, queueing, classification, retry/recovery, timeout semantics, checkpointing, or artefact content.
- Sequential/orchestrator path only; scoped parallel intra-device progress is explicitly out of scope (per-device streaming already lands via PHASE-077A; parallel intra-device lines are a follow-on).
- No timestamps introduced in this phase (console.log timestamping is a separate observability item; see OPEN QUESTIONS).
- Progress line format: `[verbose] <device>: <message>` consistent with existing PHASE-073 lines.

KNOWN RISKS:
- Additional console noise under verbose; bounded to one line per wait point.
- Progress lines interleave with existing PHASE-073 per-device lines; ordering remains deterministic in the sequential path.

OUTSTANDING RISKS:
- Parallel/scoped path still silent within a device (follow-on candidate).
- console.log lines carry no timestamps, so long-gap measurement remains manual (open question).

OPEN QUESTIONS:
- Whether console capture should gain per-line timestamps in a future observability phase (deferred; not in scope).
