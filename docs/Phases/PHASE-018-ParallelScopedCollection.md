PHASE:
ParallelScopedCollection

FILES:
app/parallel_collector.py
app/cli.py
requirements.txt
tests/test_parallel_collector.py

ACCEPTANCE CRITERIA:
- Concurrent collection only activates when --target-device scoping (allowed_devices) is set; unscoped recursive runs remain fully sequential.
- --max-concurrent flag bounds simultaneous SSH sessions (sensible default, e.g. 5).
- Checkpoint emission and resume semantics from PHASE-017B are unchanged.
- Deterministic result aggregation regardless of completion order (sorted by device name in bundle_manifest.json).

CONSTRAINTS:
- New dependency (asyncssh) requires DDR approval (DD-005) before implementation proceeds.
- No changes to build_troubleshooting_scope(), traverse_topology(), or checkpoint JSON format.
- Sequential path (no --target-device) must remain byte-for-byte behaviourally identical.

KNOWN RISKS:
- asyncssh introduces a new dependency surface (security/maintenance).
- Concurrent sessions could still stress AAA if --max-concurrent is set too high by the user.

OUTSTANDING RISKS:
- Cross-workstation bootstrap validation remains pending (operational, carried forward).

OPEN QUESTIONS:
- Should --max-concurrent have an enforced upper ceiling rather than an unbounded user-supplied value?
