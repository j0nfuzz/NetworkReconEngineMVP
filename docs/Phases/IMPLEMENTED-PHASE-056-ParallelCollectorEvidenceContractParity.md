PHASE:
PHASE-056-ParallelCollectorEvidenceContractParity

STATUS:
Implemented

FILES MODIFIED:
app/parallel_collector.py
- Added `failed_command_details` and `recovered_commands` to `_build_summary()` so every parallel summary carries the sequential evidence-contract keys.
- Added `_build_command_evidence()` helper producing the 15-field command_evidence structure with AsyncSSH-unavailable fields set to `None`.
- Wrapped individual command execution with `time.perf_counter()` to record `elapsed_seconds` without changing concurrency, ordering, or error handling.
- Populated `failed_command_details` for non-zero exits and connection-level exceptions; `recovered_commands` remains `[]` because recovery is sequential-only per DD-007.

tests/test_parallel_collector.py
- Added `test_parallel_failed_command_details_recorded` asserting failed-command evidence exists, uses the expected schema, and leaves AsyncSSH-only fields as `None`.
- Added `test_parallel_failed_command_schema_matches_sequential` proving parallel and sequential bundle summaries expose identical evidence-contract key sets for equivalent failures.
- Added `test_parallel_command_exception_records_error_type` covering exception-based command failures.

TESTS ADDED:
tests/test_parallel_collector.py::test_parallel_failed_command_details_recorded
tests/test_parallel_collector.py::test_parallel_failed_command_schema_matches_sequential
tests/test_parallel_collector.py::test_parallel_command_exception_records_error_type

DDR UPDATES:
UNCHANGED DD:2026-09-04

RISKS INTRODUCED:
- Slightly larger parallel-bundle JSON payloads when commands fail.

RISKS RESOLVED:
- Parallel collector summaries no longer omit `failed_command_details`/`recovered_commands`, removing path-specific handling burden from downstream consumers.

OPEN ISSUES:
- Recovery instrumentation parity for the parallel path remains explicitly out of scope; DD-007's single-retry recovery is still sequential-only.
