PHASE:
PHASE-010B-CheckpointFailurePersistenceRemediation

STATUS:
Implemented

FILES MODIFIED:
- app/orchestrator.py
- tests/test_checkpoint.py

TESTS ADDED:
- test_failed_collection_is_checkpointed
- test_resume_preserves_previously_failed_devices

DDR UPDATES:
UNCHANGED DD:2026-08-04

RISKS INTRODUCED:
- None.

RISKS RESOLVED:
- Failed collection state is now persisted through the checkpoint callback before continuing.
- Previously failed devices are preserved across resume.

OPEN ISSUES:
- None.
