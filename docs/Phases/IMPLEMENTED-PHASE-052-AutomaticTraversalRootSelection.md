# IMPLEMENTED-PHASE-052-AutomaticTraversalRootSelection

## Phase
PHASE-052-AutomaticTraversalRootSelection

## Status
Implemented

## Objective
Align CLI traversal behaviour with the project goal of pointing the tool at one device and receiving a complete troubleshooting package. `--target-device` becomes the traversal root automatically, recursive discovery is enabled by default, and `--no-recurse` provides an explicit opt-out.

## Files Modified
- `app/cli.py`
  - Added `--no-recurse` flag.
  - Retained `--recursive` as a backward-compatible alias/no-op.
  - Changed recursion default: collection is now recursive whenever devices are present and `--no-recurse` is absent.
  - `--target-device` now enters recursive traversal directly; it no longer requires `--recursive` to be supplied first.
  - Preserved `--scope-depth`, `--checkpoint-file`, `--max-concurrent`, and cycle-safe BFS behaviour.
- `tests/test_cli.py`
  - Updated existing non-recursive tests to use `--no-recurse` so they continue to exercise flat collection under the new default.
  - Updated direct `argparse.Namespace` construction in `_run_cli_collection` tests to include `no_recurse=True` and `scope_depth`.
  - Added PHASE-052 regression tests:
    - `test_parse_args_no_recurse_disables_recursion`
    - `test_parse_args_recursive_is_backward_compatible_alias`
    - `test_default_recursion_enabled_uses_first_device`
    - `test_no_recurse_runs_flat_collection`
    - `test_target_device_becomes_traversal_root_without_topology`
    - `test_target_device_with_topology_uses_scoped_collection`
- `tests/test_scope.py`
  - Added `test_build_troubleshooting_scope_empty_topology_returns_target_only` to guard the no-topology fallback used by `--target-device` scoping.

## Tests Added
- `tests/test_cli.py::test_parse_args_no_recurse_disables_recursion`
- `tests/test_cli.py::test_parse_args_recursive_is_backward_compatible_alias`
- `tests/test_cli.py::test_default_recursion_enabled_uses_first_device`
- `tests/test_cli.py::test_no_recurse_runs_flat_collection`
- `tests/test_cli.py::test_target_device_becomes_traversal_root_without_topology`
- `tests/test_cli.py::test_target_device_with_topology_uses_scoped_collection`
- `tests/test_scope.py::test_build_troubleshooting_scope_empty_topology_returns_target_only`

## DDR Updates
DD-014 (Proposed)
- `--target-device` becomes the traversal root directly without requiring a pre-existing `topology.json`.
- Recursive collection defaults to enabled; disabled via `--no-recurse`.
- `--recursive` retained as backward-compatible no-op/alias.
- Status remains Proposed pending GPT Reviewer approval.

## Validation Results
- `python -m pytest tests/test_cli.py tests/test_scope.py -q`: 114 passed
- `python -m pytest tests -q`: 237 passed
- `git diff --check`: clean

## Risks Introduced
- Default behaviour change: existing automation that relied on flat collection by omitting `--recursive` will now recurse unless `--no-recurse` is supplied. Mitigated by retaining `--recursive` as a no-op and providing `--no-recurse`.

## Risks Resolved
- Eliminates the need for users to know about and supply `--recursive` to obtain a complete package from a single target device.
- Removes the hidden dependency on a pre-existing `topology.json` to begin traversal from `--target-device`.

## Open Issues
- None.

## Next Recommended Action
- GPT Reviewer approval of DD-014.
- Commit PHASE-052 implementation and proceed to the next Architect-selected phase.
