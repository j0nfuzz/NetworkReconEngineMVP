# IMPLEMENTED-PHASE-073-RecursiveCollectionPerDeviceProgressLogging.md

## Phase

PHASE-073-RecursiveCollectionPerDeviceProgressLogging

## Root Cause

PHASE-071 field evidence showed recursive collection completed successfully but provided no meaningful operator-visible progress during execution. The non-recursive path already logs `[verbose] Starting device: ...` before each device, but `_run_recursive_cli()` only emitted `[verbose] Finished collection for {name}: ...` after collection returned, leaving a silent window equal to the entire recursive run.

## Logging Behaviour

### Before

```text
[verbose] Finished collection for seed-sw: collected
```

No per-device start line.

### After

```text
[verbose] Starting device: seed-sw (10.0.0.1)
[verbose] Finished collection for seed-sw: collected
```

Per-device start line is emitted in the same loop that writes the finished line.

## Files Changed

- `app/cli.py`
- `tests/test_cli.py`

## Changes

- In `_run_recursive_cli()`, added `log_verbose(f"[verbose] Starting device: {name} ({bundle.summary.get('hostname', '')})")` immediately before the existing finished-collection log.
- Preserves all existing finished-collection logging.
- Preserves collection, traversal, checkpoint, and classification behaviour.
- Added regression test proving recursive verbose output contains both start and finish lines.

## Validation

- `python -m py_compile app/discovery.py app/cli.py` passed.
- `python -m pytest tests/test_discovery.py tests/test_cli.py -q` passed: 125 passed.
- `python -m pytest -q` passed: 327 passed, 1 warning (pre-existing).

## Scope Confirmation

- No changes to `run_recursive_collection()`.
- No changes to `run_parallel_scoped_collection()`.
- No changes to `classify_neighbors()`.
- No SSH/probe logic changes.
- No checkpoint behaviour changes.
- Observability-only change.
