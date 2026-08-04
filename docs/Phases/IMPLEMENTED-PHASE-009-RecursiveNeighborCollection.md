PHASE:
PHASE-009-RecursiveNeighborCollection

STATUS:
Implemented

FILES MODIFIED:
- app/orchestrator.py (new)
- tests/test_orchestrator.py (new)

TESTS ADDED:
- test_seed_only_no_neighbors
- test_supported_neighbor_enqueued_and_collected
- test_unsupported_neighbor_recorded_not_connected
- test_visited_neighbor_not_requeued
- test_neighbor_missing_ip_skipped
- test_failed_collection_path
- test_default_credentials_applied_to_neighbors

DDR UPDATES:
UNCHANGED DD:2026-08-04

RISKS INTRODUCED:
- Plaintext default credentials propagated to discovered neighbors (homogeneous-credential assumption, accepted PoC limitation).
- max_devices guard prevents unbounded collection but does not persist state.

RISKS RESOLVED:
- None.

OPEN ISSUES:
- None.
