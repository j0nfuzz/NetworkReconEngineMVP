REVIEW VERDICT:
Not Approved

FINDINGS REVIEWED:
- PHASE-055's generic-overwrite regression is remediated: an unrecognized
  probe returns `confidence=0`, which cannot overwrite configured or
  higher-confidence pre-populated identity metadata.
- The duplicate `show version` execution is remediated: probe and collection
  use one asyncssh session, and the probe output is retained in `raw_outputs`.
- `tests/test_parallel_collector.py` is restored as newline-delimited,
  importable Python source and compiles successfully.
- Independent validation reproduced the reported results:
  `python -m py_compile app/parallel_collector.py tests/test_parallel_collector.py`
  succeeded; the parallel collector suite passed 23 tests; the full suite
  passed 277 tests with the expected existing vendor-profile fallback warning.

CRITICAL ISSUES:
None

MAJOR ISSUES:
Issue:
`_collect_device()` executes and retains the probe's `show version` command,
but skips it in the collection loop without incrementing
`summary["commands_run"]`.

Why It Matters:
The summary under-reports executed profile commands by one for every successful
parallel collection. This breaks the existing command-count invariant: the
sequential collector reports the full profile command count. The omitted probe
is a real read-only command whose output is retained as collection evidence.

Recommended Fix:
Increment `summary["commands_run"]` when the successful probe is reused as a
profile `show version` result, and add a regression assertion that the count
matches the number of profile commands/evidence entries.

REQUIREMENTS TRACEABILITY:
- Positive-confidence overwrite only: met. The implementation requires both
  positive probe confidence and a value strictly greater than existing identity
  confidence before replacing vendor/identity metadata.
- Preserve configured vendor/profile on an ambiguous probe: met and covered by
  `test_parallel_collect_device_preserves_configured_vendor_on_ambiguous_probe`.
- Reuse `show version` or justify duplicates: met. A single session is used;
  `test_parallel_collect_device_reuses_show_version_output` proves one command
  invocation and retained output.
- Restore importable test source: met. Independent `py_compile` succeeds.
- Preserve positive ArubaOS-CX behavior: met. The existing ArubaOS-CX profile
  test passes and the code supplies the resolved platform to
  `get_vendor_commands()`.
- Full suite passes: met, but insufficient to approve because it does not
  assert the command-count contract.
- Phase scope: met. The source delta is limited to the parallel collector and
  its tests; no traversal, checkpoint, credential, sequential collector, or
  transport/recovery behavior changed.

TEST ASSESSMENT:
The tests cover ambiguous identity preservation, configured-vendor retention,
ArubaOS-CX selection, failed probes, and duplicate-command removal. They omit
the resulting `commands_run` accounting invariant, allowing the major defect
above to pass all validation.

DD-012 COMPLIANCE ASSESSMENT:
Compliant. After a positive ArubaOS-CX identity probe, `_collect_device()`
passes `vendor="aruba"` and `platform="arubaos-cx"` to
`get_vendor_commands()`, preserving DD-012 platform-aware profile selection on
the parallel / `--target-device` path.

DDR REVIEW:
UNCHANGED DD:[2026-09-04]

SCALE IMPACT:
The undercount is per collected device and therefore grows linearly with
parallel traversal size; it does not introduce concurrency or race behavior.

CONCURRENCY IMPACT:
No new concurrency risk identified. The probe and profile commands run through
the same per-device connection under the existing collector semaphore.

SECURITY IMPACT:
No new security risk identified. `show version` remains validated by the
existing read-only command policy through the selected profile.

RECOVERY IMPACT:
No checkpoint/resume or retry/recovery logic changed. Incorrect command counts
can, however, make incomplete field evidence harder to recognize.

RESIDUAL RISKS:
- PHASE-055B is required to restore `commands_run` accuracy before PHASE-055
  can close.
- ArubaOS-CX LLDP parsing remains tracked in PHASE-058.
- Parallel evidence-contract parity remains tracked in PHASE-056.
- Partial-status health-score handling remains tracked in PHASE-057.

OPEN QUESTIONS:
None

RECOMMENDED NEXT PHASE:
DefaultPathIdentityCommandCountRemediation

STABLE CHECKPOINT:
NOT A STABLE CHECKPOINT

PUSH DECISION:
DO NOT PUSH

Reason:
The remediation leaves the parallel-collection summary internally inaccurate,
and required review approval has not been obtained.
