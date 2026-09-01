PHASE:
ParallelScopedCollectionRemediation

STATUS:
Implemented

FILES MODIFIED:
- app/parallel_collector.py
- tests/test_parallel_collector.py
- docs/PROJECT-JOURNAL.md

TESTS ADDED:
- tests/test_parallel_collector.py::test_non_positive_max_concurrent_normalized (parametrized for 0, -1, -5)
- tests/test_parallel_collector.py::test_wave_respects_max_devices_capacity

DDR UPDATES:
UNCHANGED DD:DD-005

RISKS INTRODUCED:
None beyond existing PHASE-018 accepted risks.

RISKS RESOLVED:
- Non-positive --max-concurrent no longer stalls collection.
- Parallel waves no longer exceed max_devices remaining capacity.

OPEN ISSUES:
- Whether --max-concurrent should have an enforced upper ceiling remains unresolved.
