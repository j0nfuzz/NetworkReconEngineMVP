PHASE:
DefaultPathIdentityCommandCountRemediation

STATUS:
Implemented

FILES MODIFIED:
app/parallel_collector.py
- In `_collect_device()`, when the successful identity probe's `show version`
  output is reused for the profile's `show version` evidence, the code now
  increments `summary["commands_run"]` exactly once for that command.
- The collection loop still skips the explicit `show version` run to preserve
  the single-execution behavior.
- All confidence-gating, identity overwrite, vendor propagation, and platform
  selection logic from PHASE-055A remains unchanged.

tests/test_parallel_collector.py
- Added `test_parallel_collect_device_commands_run_includes_reused_show_version`
  to assert that `commands_run` equals the number of profile commands/evidence
  entries when the probe's `show version` is reused.
- Updated `test_parallel_collect_device_reuses_show_version_output` to also
  assert `bundle.summary["commands_run"] == len(bundle.raw_outputs)`.

TESTS ADDED OR UPDATED:
- tests/test_parallel_collector.py::test_parallel_collect_device_commands_run_includes_reused_show_version (new)
- tests/test_parallel_collector.py::test_parallel_collect_device_reuses_show_version_output (updated)

DDR UPDATES:
UNCHANGED DD:[2026-09-04]

VALIDATION RESULTS:
- `python -m py_compile app/parallel_collector.py tests/test_parallel_collector.py` → success
- `python -m pytest tests/test_parallel_collector.py -q` → 24 passed
- `python -m pytest tests -q` → 278 passed, 1 warning

REVIEWER FINDINGS ADDRESSED:
- The reused successful identity probe `show version` is now counted in
  `summary["commands_run"]` exactly once.
- `show version` is still executed only once and its output is reused.
- No double-counting occurs.

RISKS INTRODUCED:
- None. The accounting change is a single counter increment gated by the same
  condition that records the reused output.

RISKS RESOLVED:
- Parallel collection summary no longer under-reports executed commands by one.
- Command accounting now matches the number of retained evidence outputs.

RESIDUAL RISKS:
- ArubaOS-CX neighbour discovery remains non-functional regardless of this fix
  (tracked in PHASE-058).
- Parallel-path evidence-contract divergence from the sequential path remains
  open (tracked in PHASE-056).
- Partial-status health scoring remains unaffected by failed commands
  (tracked in PHASE-057).
