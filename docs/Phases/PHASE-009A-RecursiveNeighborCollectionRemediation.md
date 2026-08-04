PHASE:
Recursive Neighbor Collection Remediation

FILES:
- app/orchestrator.py
- tests/test_orchestrator.py

ACCEPTANCE CRITERIA:
- Discovered neighbors in run_recursive_collection() inherit username/password/enable_password exclusively from default_credentials, never from the parent device.
- A neighbor name is never added to the collection queue more than once; queue membership is checked alongside visited set before enqueueing.
- All existing PHASE-009 behavior is otherwise preserved (supported enqueue, unsupported exclusion, missing-IP skip, failed collection handling, max_devices bound).
- Regression tests cover default credential inheritance and duplicate neighbor suppression across multiple parent discoveries.

CONSTRAINTS:
- No new dependencies.
- No traverse_topology() integration.
- No concurrency, checkpointing, or vault changes.
- No Device dataclass changes.

KNOWN RISKS:
- None.

OUTSTANDING RISKS:
- Plaintext default credentials remain an accepted PoC limitation.

OPEN QUESTIONS:
- None.
