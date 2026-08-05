PHASE:
Checkpoint Failure Persistence Remediation

FILES:
- app/orchestrator.py
- tests/test_checkpoint.py

ACCEPTANCE CRITERIA:
- run_recursive_collection() invokes on_collected checkpoint callback after recording a failed collection status, before proceeding to the next iteration.
- The checkpoint written after a failed collection includes the updated failed list and all other current state (visited, queued/pending, successful, unsupported).
- Successful collection callback timing and behavior remain unchanged.
- Resume behavior from PHASE-010A remains unchanged.
- Checkpoint JSON format remains unchanged.
- Tests cover: failed collection triggers checkpoint callback, failed state survives save/load round-trip, resume preserves previously failed devices, and successful-path checkpoint still includes newly queued neighbors.

CONSTRAINTS:
- No new dependencies.
- No concurrency, encryption, database persistence.
- No Device dataclass changes.
- No checkpoint format changes.
- Minimal additive changes only.

KNOWN RISKS:
- None.

OUTSTANDING RISKS:
- Plaintext JSON checkpoint remains unencrypted.
- Concurrent checkpoint writes remain unaddressed.

OPEN QUESTIONS:
- None.
