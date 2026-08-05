PHASE:
Checkpointing

FILES:
- app/checkpoint.py (new)
- tests/test_checkpoint.py (new)

ACCEPTANCE CRITERIA:
- New functions to save and load checkpoint state as JSON: e.g. `save_checkpoint(path, state)` and `load_checkpoint(path)`.
- Checkpoint state captures exactly the fields already produced by `run_recursive_collection()`: visited device names, pending (queued-but-not-yet-collected) device names, successful, failed, unsupported.
- `save_checkpoint()` is callable after each device collection in the recursive loop (integration point only — no forced call site changes required beyond exposing state at each iteration).
- `load_checkpoint()` returns a structure that can be used to resume `run_recursive_collection()` without re-collecting already-visited devices.
- Missing/corrupt checkpoint file raises a clear error or returns None (implementer's choice, document in IMPLEMENTED file) rather than crashing ambiguously.
- No changes to existing `run_recursive_collection()` return shape or default behaviour when no checkpoint is supplied (backward compatible).
- Tests cover: save then load round-trip preserves all fields, loading a missing file, resuming skips already-visited devices.

CONSTRAINTS:
- No new dependencies (use built-in `json`).
- No concurrency changes (Wishlist Phase 9, out of scope — deferred due to `asyncssh` dependency conflict with governance).
- No encryption/vault.
- No Device dataclass changes.
- Minimal, additive integration with app/orchestrator.py only if required to expose resumable state; do not restructure the existing traversal/collection loop.

KNOWN RISKS:
- None beyond those already carried.

OUTSTANDING RISKS:
- Checkpoint files are plaintext JSON and may contain device names/IPs (no credentials are stored, consistent with PHASE-008/009A scope).
- Concurrent writes to the same checkpoint file are not addressed (single-process PoC assumption).

OPEN QUESTIONS:
- None.
