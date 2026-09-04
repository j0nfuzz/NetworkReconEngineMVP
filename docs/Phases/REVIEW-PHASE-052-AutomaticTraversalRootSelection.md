# REVIEW-PHASE-052-AutomaticTraversalRootSelection

## Review Result
Not Approved

## Critical Issues
Issue: The no-`topology.json` path sets `allowed_devices` to `{target_device}` and selects `run_parallel_scoped_collection`.

Why It Matters: That collector skips every discovered neighbour outside `allowed_devices`, so a target-only invocation collects only the root rather than the required complete troubleshooting package.

Recommended Fix: Preserve the target as the seed but select a traversal path that can enqueue newly discovered neighbours; add a regression test proving a discovered neighbour is collected without a prior topology file.

## Major Issues
None

## Requirements Assessment
- Target selection, default recursion, `--no-recurse`, and `--recursive` compatibility are implemented.
- The required no-topology discovery expansion is not implemented; scope-depth, checkpoint/resume, bounded concurrency, and BFS preservation cannot establish compliance for that path.

## Validation Assessment
- `python -m pytest tests/test_cli.py tests/test_scope.py -q`: 114 passed.
- `git diff --check`: clean.
- The focused tests do not exercise or prove no-topology neighbour expansion.

## DDR Review
Decision ID: DD-014

Rejected

Reason: The fixed target-only allow-list contradicts the decision's required recursive expansion from a target root without prior topology state.

## Outstanding Risks
- Default recursion can unexpectedly broaden collections; `--no-recurse` mitigates this.

## Open Questions
None

## Recommended Next Phase
AutomaticTraversalRootExpansionRemediation

## Checkpoint Status
DO NOT PUSH

Reason: PHASE-052 does not meet its core traversal-expansion acceptance criterion and DD-014 is rejected.