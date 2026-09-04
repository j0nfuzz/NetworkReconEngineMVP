PHASE:
AutomaticTraversalRootExpansionRemediation

FILES:
app/cli.py
app/parallel_collector.py
tests/test_cli.py
tests/test_parallel_collector.py

ACCEPTANCE CRITERIA:
- When `--target-device` is supplied and no `topology.json` exists, the scoped parallel collector enqueues newly discovered neighbours instead of collecting only the target device.
- `run_parallel_scoped_collection_async`/`run_parallel_scoped_collection` accept `allowed_devices=None` to mean unbounded neighbour discovery, mirroring the existing `is not None` guard pattern already used in `app/orchestrator.py::run_recursive_collection`; the current unconditional `ValueError` on `allowed_devices=None` is removed.
- When `topology.json` exists, `--scope-depth`-bounded `allowed_devices` behaviour (computed via `build_troubleshooting_scope()`) is unchanged.
- Cycle-safe visited/queued tracking, checkpoint/resume persistence, and bounded concurrency (semaphore/`--max-concurrent`) are unchanged.
- New/updated tests prove: (a) a discovered neighbour is actually collected when `--target-device` is used without a prior `topology.json`, (b) topology-bounded scope-depth behaviour is unchanged, (c) `run_parallel_scoped_collection_async(allowed_devices=None)` no longer raises and instead discovers neighbours.
- Full regression suite passes (`python -m pytest tests -q`).

CONSTRAINTS:
- Do not modify `build_troubleshooting_scope()` or its BFS/cycle-safety semantics (`app/scope.py` out of scope).
- Do not change the semaphore/`max_concurrent` bounded-concurrency mechanism itself.
- Do not change checkpoint/resume persistence format (`app/checkpoint.py` out of scope).
- Do not reopen PHASE-047/PHASE-051 (vendor command-profile changes out of scope).
- No SSH, credential, or provenance changes.

KNOWN RISKS:
- Removing the `ValueError` guard changes `run_parallel_scoped_collection_async`'s contract; `app/cli.py` is currently its only caller and must be updated in the same change.
- Unbounded discovery from a target root with no topology is still bounded only by `max_devices`, not by any hop/device-count safeguard (carried from PHASE-052 open question).

OUTSTANDING RISKS:
- No device-count/confirmation safeguard exists before recursion expands from a target root (carried from PHASE-052).
- Running-config completeness and ArubaOS-CX command coverage expansion remain deferred (carried, unrelated).

OPEN QUESTIONS:
- Should the no-topology discovery path persist a `topology.json` snapshot as it discovers neighbours, to bound/accelerate subsequent runs? (deferred to a later phase)
