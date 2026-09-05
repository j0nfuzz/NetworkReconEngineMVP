PHASE:
ParallelCollectorEvidenceContractParity

FILES:
app/parallel_collector.py
tests/test_parallel_collector.py

ACCEPTANCE CRITERIA:
- `_collect_device()` records `failed_command_details` (command, error_type, elapsed_seconds) for failed commands, using the same field names already emitted by `app/collector.py`'s `command_evidence`.
- Bundle summaries produced by the parallel path carry the same summary keys as the sequential path (`failed_command_details` populated; `recovered_commands` present as an empty list, since recovery is out of scope here) so downstream consumers (health scoring, bundle writers) do not require path-specific handling.
- A regression test asserts summary-key parity between a sequential bundle and a parallel bundle for an equivalent failed command.

CONSTRAINTS:
- Do not implement retry/recovery in the parallel path; DD-007's single-retry policy applies only to the sequential Paramiko session.
- Do not change asyncssh concurrency, semaphore, or wave-scheduling logic.
- Fields unavailable via asyncssh (e.g. Paramiko channel/transport introspection) must be recorded as `None`, not fabricated.

KNOWN RISKS:
- asyncssh does not expose the same channel/transport state as Paramiko; `transport_state`/`channel_state` will be `None` on this path, a known and documented asymmetry rather than a defect to silently mask.

OUTSTANDING RISKS:
- None resolved beyond stated scope; recovery-instrumentation parity remains explicitly out of scope.

OPEN QUESTIONS:
- Should retry/recovery ever be added to the parallel path, or should recovery remain sequential-only by design? Deferred; raise as a DDR proposal only if a future phase needs to answer it.
