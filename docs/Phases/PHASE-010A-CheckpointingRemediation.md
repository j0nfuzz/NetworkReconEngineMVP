PHASE:
Checkpointing Remediation

FILES:
- app/checkpoint.py
- app/orchestrator.py
- tests/test_checkpoint.py

ACCEPTANCE CRITERIA:
- run_recursive_collection() accepts an optional resume_state dict (visited, pending, successful, failed, unsupported) and initializes internal state from it.
- Device names in resume_state["visited"] are never collected again when passed as discovered neighbors.
- Device names in resume_state["pending"] are reconstructed as Device objects with vendor "unknown" and credentials from default_credentials; their hostnames are looked up from neighbor records when available, otherwise left empty.
- Checkpoint persistence (on_collected callback) occurs after all discovered neighbors are classified, deduplicated, and enqueued.
- Existing checkpoint JSON format is unchanged.
- Existing behavior is preserved when resume_state is not supplied.
- Tests cover: resume from checkpoint skips visited device, resumes pending device, includes newly discovered neighbors in persisted pending state, and does not re-collect visited devices that appear in neighbor records.

CONSTRAINTS:
- No new dependencies.
- No concurrency, encryption, database persistence.
- No Device dataclass changes.
- Minimal additive changes only.

KNOWN RISKS:
- Pending device reconstruction from names only may lack IP when not also discovered as a neighbor; accepted PoC limitation.

OUTSTANDING RISKS:
- Plaintext JSON checkpoint remains unencrypted.
- Concurrent checkpoint writes remain unaddressed.

OPEN QUESTIONS:
- None.
