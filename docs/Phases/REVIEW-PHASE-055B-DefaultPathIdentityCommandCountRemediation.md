REVIEW VERDICT:
Approved

FINDINGS REVIEWED:
- The PHASE-055A accounting defect was correctly diagnosed: a successful
  identity-probe `show version` was retained as evidence but excluded from the
  counter because the collection loop skipped it.
- PHASE-055B increments `summary["commands_run"]` only when the probe result is
  reused for a selected profile containing `show version`.
- The loop then skips `show version`, leaving exactly one execution and exactly
  one counter increment.

CRITICAL ISSUES:
None

MAJOR ISSUES:
None

TEST ASSESSMENT:
- `test_parallel_collect_device_commands_run_includes_reused_show_version`
  covers an ArubaOS-CX detection path and proves one `show version` invocation,
  retained output, DD-012 vendor/platform propagation, and command-count parity.
- `test_parallel_collect_device_reuses_show_version_output` also asserts
  `commands_run == len(raw_outputs)`, protecting the reuse path from another
  undercount.
- Existing PHASE-055/055A tests continue to cover positive identity selection,
  ambiguous-probe vendor preservation, and failed probe handling.
- Independent validation reproduced:
  - `python -m py_compile app/parallel_collector.py tests/test_parallel_collector.py` succeeded.
  - `python -m pytest tests/test_parallel_collector.py -q` passed: 24 tests.
  - `python -m pytest tests -q` passed: 278 tests, 1 existing warning from the vendor-profile fallback test.

DD-012 COMPLIANCE ASSESSMENT:
Compliant. The accounting change does not alter identity confidence gating or
vendor/platform propagation; the regression test confirms detected
`vendor="aruba"` and `platform="arubaos-cx"` remain available to profile
selection.

SCALE IMPACT:
The corrected counter applies independently per device and introduces no new
scaling concern.

CONCURRENCY IMPACT:
No new concurrency risk. The counter remains local to each `_collect_device()`
invocation and the existing semaphore behavior is unchanged.

SECURITY IMPACT:
No new security risk. The same read-only `show version` probe is reused.

RECOVERY IMPACT:
No checkpoint, retry, or recovery behavior changed. Summary accounting now
matches retained successful command evidence.

DDR REVIEW:
UNCHANGED DD:[2026-09-04]

OUTSTANDING RISKS:
- ArubaOS-CX LLDP parsing remains tracked in PHASE-058.
- Parallel-path evidence-contract parity remains tracked in PHASE-056.
- Partial-status health-score handling remains tracked in PHASE-057.

OPEN QUESTIONS:
None

RECOMMENDED NEXT PHASE:
ParallelCollectorEvidenceContractParity

STABLE CHECKPOINT:
STABLE CHECKPOINT

COMMIT MESSAGE:
PHASE-055B: correct reused identity probe command accounting

PUSH DECISION:
PUSH RECOMMENDED

COMMANDS:
git add app/parallel_collector.py tests/test_parallel_collector.py docs/PROJECT-JOURNAL.md docs/Phases/PHASE-055-DefaultPathIdentityAndPlatformPropagation.md docs/Phases/IMPLEMENTED-PHASE-055-DefaultPathIdentityAndPlatformPropagation.md docs/Phases/REVIEW-PHASE-055-DefaultPathIdentityAndPlatformPropagation.md docs/Phases/PHASE-055A-DefaultPathIdentityAndPlatformPropagationRemediation.md docs/Phases/IMPLEMENTED-PHASE-055A-DefaultPathIdentityAndPlatformPropagationRemediation.md docs/Phases/REVIEW-PHASE-055A-DefaultPathIdentityAndPlatformPropagationRemediation.md docs/Phases/PHASE-055B-DefaultPathIdentityCommandCountRemediation.md docs/Phases/IMPLEMENTED-PHASE-055B-DefaultPathIdentityCommandCountRemediation.md docs/Phases/REVIEW-PHASE-055B-DefaultPathIdentityCommandCountRemediation.md
git commit -m "PHASE-055B: correct reused identity probe command accounting"
git push
