PHASE:
DefaultPathIdentityAndPlatformPropagation

FILES:
app/cli.py
app/parallel_collector.py
tests/test_cli.py
tests/test_parallel_collector.py

ACCEPTANCE CRITERIA:
- Before command selection, `_collect_device()` (app/parallel_collector.py) performs the same identity probe (`show version` + `identify_device()` + `classify_role()`) that the non-recursive CLI branch already performs, populating `device.metadata["identity"]`/`["role"]`.
- `_collect_device()` passes the resolved `platform` into `get_vendor_commands()`, matching the existing call in `app/collector.py`.
- A regression test proves an ArubaOS-CX device reached via `--target-device` with no pre-existing `topology.json` selects the `aruba-cx` profile, not `generic`.
- `run_recursive_collection` (sequential, non-`--target-device` recursive path) and the flat single-device path are unchanged; full existing suite continues to pass.

CONSTRAINTS:
- No changes to BFS/traversal, checkpoint/resume, credential merging, or SSH transport/retry/recovery logic.
- Detection probe command must pass `validate_read_only_command()`.
- Do not alter `run_recursive_collection`'s existing identity handling (already correct per app/cli.py `_run_recursive_cli` -> `execute_device_collection`).

KNOWN RISKS:
- One additional SSH round trip (probe) per device increases parallel collection time.
- Detection heuristics may misclassify platform; this is a pre-existing risk in app/detector.py, not introduced here.

OUTSTANDING RISKS:
- ArubaOS-CX neighbour discovery remains non-functional regardless of this fix (tracked in PHASE-058).
- Parallel-path evidence-contract divergence from the sequential path remains open (tracked in PHASE-056).

OPEN QUESTIONS:
- None.
