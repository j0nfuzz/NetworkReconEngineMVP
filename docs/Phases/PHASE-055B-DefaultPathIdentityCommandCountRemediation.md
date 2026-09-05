PHASE:
DefaultPathIdentityCommandCountRemediation

FILES:
app/parallel_collector.py
tests/test_parallel_collector.py

ACCEPTANCE CRITERIA:
- When a successful identity probe is reused as the selected profile's
  `show version` evidence, `_collect_device()` counts it in
  `summary["commands_run"]` exactly once.
- A regression test proves `summary["commands_run"]` equals the selected
  profile command count for successful collection with reused `show version`
  output.
- The regression preserves PHASE-055A's one-session and one-`show version`
  execution behavior.
- `python -m pytest tests/test_parallel_collector.py -q` and
  `python -m pytest tests -q` pass.

CONSTRAINTS:
- Do not change identity confidence gating, vendor/platform selection,
  traversal, checkpoint/resume, credentials, or SSH transport/retry/recovery
  behavior.
- Do not modify `app/collector.py` or sequential-path behavior.

KNOWN RISKS:
- None beyond the existing parallel-path evidence-contract divergence tracked
  in PHASE-056.

OUTSTANDING RISKS:
- ArubaOS-CX neighbour discovery remains non-functional regardless of this fix
  (PHASE-058).
- Parallel-path evidence-contract divergence remains open (PHASE-056).
- Partial-status health-score handling remains open (PHASE-057).

OPEN QUESTIONS:
- None.
