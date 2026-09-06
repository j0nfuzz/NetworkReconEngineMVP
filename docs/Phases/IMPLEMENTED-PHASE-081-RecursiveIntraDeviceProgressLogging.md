PHASE:
PHASE-081-RecursiveIntraDeviceProgressLogging

STATUS:
Implemented

ROOT CAUSE:
- FT060920261933 console.log contained only per-device Starting/Finished lines (PHASE-073 granularity) plus the final manifest message. All intra-device activity - SSH probe, identity probe, connect, per-command execution, auth/timeout waits - was silent, producing the long no-feedback periods observed in the field.

FILES MODIFIED:
- app/collector.py: execute_device_collection() accepts optional progress callback (default None); emits [verbose] <device>: probe/connect/(i/N) <command> lines at each wait point; identical behaviour when omitted.
- app/orchestrator.py: run_recursive_collection() accepts optional on_progress (default None); emits identity-probe phase lines consistent with PHASE-061/061A wiring; forwards progress to execute_device_collection only when supplied, preserving existing monkeypatched-collector call contracts.
- app/cli.py: sequential recursive path wires on_progress=log_verbose, routing new lines through the existing verbose/console.log capture (PHASE-077A mechanism). Parallel/scoped intra-device progress deliberately out of scope per phase constraints.

TESTS ADDED:
- tests/test_collector.py (new module, 4 tests): probe/connect/command progress emission; enumeration over the full profile count; probe-failure line; no-callback behaviour unchanged.
- tests/test_orchestrator.py: on_progress forwarding with identity-phase lines; no-callback caller contract preserved (positional-only collector invocation).
- tests/test_cli.py: sequential recursive CLI wires a callable on_progress that emits through verbose output.

VALIDATION:
- Full suite: 342 passed, 1 pre-existing warning.

UNIFIED DIFF SUMMARY:
- app/collector.py +14/-2; app/orchestrator.py +12/-1; app/cli.py +1; tests +112. No artefact, checkpoint, traversal, classification, queueing, retry/recovery, or timeout changes.

REGRESSION COVERAGE:
- All existing orchestrator/CLI/collector tests pass unmodified (conditional forwarding preserves positional-only patched collectors).
- Quiet mode verified silent by design: log_verbose emits only when verbose is set.

SCOPE CONFIRMATION:
- Logging only; sequential path only; no timestamps introduced (deferred open question); no changes to any proven subsystem from the DO-NOT-REOPEN list.

DDR UPDATES:
UNCHANGED DD:DD-008

RISKS INTRODUCED:
- Additional verbose console volume (one line per wait point).

RISKS RESOLVED:
- Operator-silence gap during active collection (FT060920261933 DEFECT 1).

OPEN ISSUES:
- Parallel/scoped intra-device progress (follow-on candidate).
- console.log line timestamps (deferred observability item).
