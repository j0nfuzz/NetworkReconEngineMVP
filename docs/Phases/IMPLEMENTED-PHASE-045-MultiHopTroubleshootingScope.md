PHASE:
MultiHopTroubleshootingScope

STATUS:
Implemented

FILES MODIFIED:
- app/scope.py
  - Added optional `hops` parameter to `build_troubleshooting_scope(topology, target, hops=1)`.
  - Default `hops=1` preserves existing single-hop behaviour (target + direct neighbours).
  - `hops=0` and negative values return target-only.
  - Implemented bounded, cycle-safe breadth-first traversal using a visited set and distance-limited queue.
  - Maintains deterministic sorted output ordering.
  - Unknown targets still return `[target]` without raising, regardless of `hops`.
- app/cli.py
  - Added `--scope-depth` integer argument (default `1`).
  - `--scope-depth` is passed through to `build_troubleshooting_scope()` as `hops` only when `--target-device` is supplied; otherwise it has no effect.
  - Updated `_run_recursive_cli()` signature to accept `scope_depth: int = 1`.
- tests/test_scope.py
  - Added regression tests for `hops=0`, 2-hop traversal, 3-hop chain traversal (Wishlist Phase 14 example), cycle safety with a large hop count, disconnected graph segments, unknown target with hops, negative hops, deterministic multi-hop output.
  - Added CLI wiring tests for `--scope-depth` with `--target-device`, `--scope-depth` without `--target-device`, and default single-hop behaviour when `--scope-depth` is omitted.

TESTS ADDED:
- tests/test_scope.py (17 new tests, 23 total in file)

DDR UPDATES:
- DD-011 unchanged (Proposed, pending GPT Reviewer approval)

VALIDATION RESULTS:
- Targeted scope tests: 23 passed
- Full primary test suite: 214 passed

RISKS INTRODUCED:
- Larger `hops` values on dense topologies can expand the scoped device set significantly; this is an explicit engineer-controlled trade-off via `--scope-depth`.

RISKS RESOLVED:
- Wishlist Phase 14's multi-hop topology-aware troubleshooting example is now supported.
- Single-hop default behaviour and all existing tests remain unchanged.

OPEN ISSUES:
- DD-007 remains inconclusively validated on real hardware.
- DD-011 requires GPT reviewer approval to become authoritative.
