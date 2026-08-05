PHASE:
PHASE-010A-CheckpointingRemediation

STATUS:
Implemented

FILES MODIFIED:
- app/checkpoint.py
- app/orchestrator.py
- tests/test_checkpoint.py

TESTS ADDED:
- test_resume_from_checkpoint_skips_visited_and_collects_pending
- test_checkpoint_callback_includes_newly_discovered_neighbors
- Updated test_on_collected_callback_receives_state for new callback timing

DDR UPDATES:
UNCHANGED DD:2026-08-04

RISKS INTRODUCED:
- Pending device reconstruction from names may lack hostname if neighbor records are unavailable (accepted PoC limitation).

RISKS RESOLVED:
- run_recursive_collection() can now consume loaded checkpoint state and skip already visited devices.
- Checkpoint callback now fires after discovery/enqueue processing, capturing accurate pending state.

OPEN ISSUES:
- None.
