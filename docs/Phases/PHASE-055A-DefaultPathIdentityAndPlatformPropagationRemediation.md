PHASE:
DefaultPathIdentityAndPlatformPropagationRemediation

FILES:
app/parallel_collector.py
tests/test_parallel_collector.py

ACCEPTANCE CRITERIA:
- `_collect_device()` only overwrites `device.vendor`/`device.metadata["identity"]` when `identify_device()` returns positive confidence; an unrecognized/ambiguous probe result preserves the existing configured vendor and metadata instead of downgrading to `generic`.
- The identity probe's `show version` result is reused as the collection profile's `show version` evidence (or the two-session/duplicate-command behavior is explicitly justified and covered by a test if retained).
- `tests/test_parallel_collector.py` is restored to valid, newline-delimited, importable source; `python -m py_compile tests/test_parallel_collector.py` succeeds.
- Add a regression test: a configured vendor (e.g. `cisco`) with an unrecognized/ambiguous `show version` banner keeps its configured vendor and command profile rather than falling back to `generic`.
- Full suite passes (`python -m pytest tests -q`) and results are recorded in the IMPLEMENTED file.

CONSTRAINTS:
- No changes to BFS/traversal, checkpoint/resume, credential merging, or SSH transport/retry/recovery logic.
- Do not alter `run_recursive_collection`'s existing identity handling or `app/collector.py`'s sequential-path behavior.
- Preserve PHASE-055's existing passing behavior for devices with a positively-detected identity (e.g. the ArubaOS-CX selection regression test).

KNOWN RISKS:
- Confidence-gating the vendor overwrite may leave `vendor="auto"`/unknown devices without any profile if the probe never returns positive confidence; must fall back to the existing `auto`/generic path deterministically, not silently.

OUTSTANDING RISKS:
- ArubaOS-CX neighbour discovery remains non-functional regardless of this fix (tracked in PHASE-058).
- Parallel-path evidence-contract divergence from the sequential path remains open (tracked in PHASE-056).

OPEN QUESTIONS:
- None.
