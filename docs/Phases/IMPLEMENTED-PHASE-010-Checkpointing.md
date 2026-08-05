PHASE:
PHASE-010-Checkpointing

STATUS:
Implemented

FILES MODIFIED:
- app/checkpoint.py (new)
- app/orchestrator.py
- tests/test_checkpoint.py (new)

TESTS ADDED:
- test_save_and_load_checkpoint_roundtrip
- test_load_missing_checkpoint_returns_none
- test_load_corrupt_checkpoint_raises
- test_checkpoint_content_is_plain_json
- test_state_to_checkpoint_sorted_pending
- test_on_collected_callback_receives_state
- test_resume_from_checkpoint_skips_visited

DDR UPDATES:
UNCHANGED DD:2026-08-04

RISKS INTRODUCED:
- Checkpoint files are plaintext JSON containing device names/IPs (no credentials stored).
- Concurrent writes to the same checkpoint file are not addressed (single-process PoC).

RISKS RESOLVED:
- None.

OPEN ISSUES:
- None.
