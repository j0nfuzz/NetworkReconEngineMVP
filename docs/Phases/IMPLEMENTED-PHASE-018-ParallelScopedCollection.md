PHASE:
ParallelScopedCollection

STATUS:
Implemented

FILES MODIFIED:
- app/parallel_collector.py (new)
- app/cli.py
- requirements.txt
- tests/test_parallel_collector.py (new)
- tests/test_scope.py (updated mocks for target-device CLI tests)

TESTS ADDED:
- tests/test_parallel_collector.py::test_scoped_runs_execute_concurrently
- tests/test_parallel_collector.py::test_unscoped_runs_remain_sequential
- tests/test_parallel_collector.py::test_deterministic_manifest_ordering
- tests/test_parallel_collector.py::test_checkpoint_behaviour_unchanged
- tests/test_parallel_collector.py::test_max_concurrent_limits_simultaneous_sessions

DDR UPDATES:
- Proposed DD-005: add asyncssh dependency for scoped parallel SSH collection.
  Status remains Proposed; pending GPT Reviewer approval.

RISKS INTRODUCED:
- New asyncssh dependency surface (security/maintenance).
- Concurrent sessions may stress AAA if --max-concurrent is set too high.

RISKS RESOLVED:
- Scoped target-device collection no longer forced to run sequentially across multiple devices.

OPEN ISSUES:
- Whether --max-concurrent should have an enforced upper ceiling (currently user-supplied, bounded by semaphore).
