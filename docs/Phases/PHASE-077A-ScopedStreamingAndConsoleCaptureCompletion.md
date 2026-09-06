PHASE:
PHASE-077A-ScopedStreamingAndConsoleCaptureCompletion

FILES:
- app/cli.py

ACCEPTANCE CRITERIA:
- `--target-device` (scoped/parallel) recursive collection streams each device bundle, manifest, and topology update live via the same per-device callback path used by `run_recursive_collection()`.
- `run_parallel_scoped_collection()` receives an `on_device_collected`-equivalent callback and each completed device is written to disk before the whole scoped run returns.
- The final "Generated bundle manifest" console line is routed through the same capture mechanism as other verbose output so it appears in `console.log` when recursive/verbose mode is active.
- Regression test proves scoped/parallel collection writes device bundles before the run completes.
- Regression test proves the final manifest message appears in `console.log`.

CONSTRAINTS:
- No changes to traversal, classification, queueing, or SSH behavior.
- No changes to `app/parallel_collector.py` collection/concurrency semantics; reuse its existing `on_collected` callback contract if sufficient, or add a minimal per-device hook consistent with `run_recursive_collection()`.
- No changes to `app/orchestrator.py` (already correct per Terra).

KNOWN RISKS:
- Scoped/parallel path runs devices concurrently; per-device writes must remain thread/async-safe with existing file writes.

OUTSTANDING RISKS:
- PHASE-076 (runtime provenance path) remains broken until PHASE-076A lands; tracked separately.

OPEN QUESTIONS:
- None.
