# IMPLEMENTED-PHASE-053-AutomaticTraversalRootExpansionRemediation

## Phase
PHASE-053-AutomaticTraversalRootExpansionRemediation

## Status
Implemented

## Objective
Correct the implementation defect in PHASE-052: when `--target-device` was used without a pre-existing `topology.json`, the CLI constrained the parallel collector with a fixed `{target_device}` allowed scope, preventing discovered neighbours from being traversed. This phase restores the intended one-device-to-complete-package workflow by allowing unbounded neighbour discovery in the parallel collector path.

## Files Modified
- `app/parallel_collector.py`
  - Removed the unconditional `ValueError` in `run_parallel_scoped_collection_async` when `allowed_devices=None`.
  - Changed neighbour filtering to mirror `app/orchestrator.py::run_recursive_collection`: when `allowed_devices` is `None`, discovered neighbours are eligible for queueing; when a set is provided, only members are eligible.
  - Changed pending-name filtering similarly.
  - Updated docstring to document the unbounded-discovery mode.
- `app/cli.py`
  - `_run_recursive_cli` now always routes the `--target-device` path through `run_parallel_scoped_collection`, passing `allowed_devices=None` when no `topology.json` exists.
  - When `topology.json` exists, the existing hop-limited scope is still computed via `build_troubleshooting_scope()` and passed as `allowed_devices`.
  - The non-target-device default recursive path continues to use `run_recursive_collection`.
- `tests/test_cli.py`
  - Updated `test_target_device_becomes_traversal_root_without_topology` to assert `allowed_devices is None`.
- `tests/test_scope.py`
  - Updated `test_cli_target_device_without_topology_uses_target_only` and `test_cli_target_device_selects_non_first_seed` to assert `allowed_devices is None`.
- `tests/test_parallel_collector.py`
  - Added `test_allowed_devices_none_discovers_neighbors`: proves unbounded discovery from the seed when `allowed_devices=None`.
  - Added `test_allowed_devices_none_no_longer_raises`: proves `allowed_devices=None` no longer raises `ValueError`.
  - Added `test_allowed_devices_set_still_bounds_discovery`: proves explicit `allowed_devices` sets still restrict traversal.

## Tests Added
- `tests/test_parallel_collector.py::test_allowed_devices_none_discovers_neighbors`
- `tests/test_parallel_collector.py::test_allowed_devices_none_no_longer_raises`
- `tests/test_parallel_collector.py::test_allowed_devices_set_still_bounds_discovery`

## DDR Updates
DD-015 (Proposed)
- `run_parallel_scoped_collection`/`run_parallel_scoped_collection_async` accept `allowed_devices=None` to mean unbounded neighbour discovery from the seed device.
- `app/cli.py` passes `allowed_devices=None` for `--target-device` when no `topology.json` exists, and continues to pass the hop-limited set when `topology.json` exists.
- Status remains Proposed pending GPT Reviewer approval.

## Validation Results
- `python -m pytest tests/test_cli.py tests/test_parallel_collector.py tests/test_scope.py -q`: 131 passed
- `python -m pytest tests -q`: 240 passed
- `git diff --check`: clean

## Risks Introduced
- Default recursion now expands unbounded by topology hops when `--target-device` is used without a `topology.json`; the only bound is `max_devices`. Users who want a single-device collection must pass `--no-recurse`.

## Risks Resolved
- Discovered neighbours are now eligible for traversal when starting from a target device without a pre-existing topology file, satisfying the rejected PHASE-052 acceptance criterion.
- The parallel collector's contract now matches the existing sequential orchestrator's `allowed_devices=None` semantics.

## Open Issues
- No device-count/confirmation safeguard exists before recursion expands from a target root (carried from PHASE-052).
- Running-config completeness and ArubaOS-CX command coverage expansion remain deferred (carried, unrelated).

## Next Recommended Action
- GPT Reviewer approval of DD-015 and PHASE-053; if approved, commit and select next phase.
