PHASE:
PHASE-009A-RecursiveNeighborCollectionRemediation

STATUS:
Implemented

FILES MODIFIED:
- app/orchestrator.py
- tests/test_orchestrator.py

TESTS ADDED:
- test_duplicate_neighbor_not_queued_multiple_times
- Updated test_default_credentials_applied_to_neighbors to assert defaults override parent credentials

DDR UPDATES:
UNCHANGED DD:2026-08-04

RISKS INTRODUCED:
- None.

RISKS RESOLVED:
- Discovered neighbors no longer inherit parent device credentials.
- Duplicate neighbor names are no longer queued more than once before collection.

OPEN ISSUES:
- None.
