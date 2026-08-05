REVIEW VERDICT:
Not Approved

CRITICAL ISSUES:
Issue:
Checkpoint state cannot resume `run_recursive_collection()`.

Why It Matters:
The function accepts neither loaded state nor pending devices, always creates empty `visited` state from a seed, and the resume test bypasses the checkpoint by manually starting at SW02.

Recommended Fix:
Add minimal optional resume-state input that initializes visited/pending/successful/failed/unsupported and reconstructs pending devices without re-collecting visited names.

MAJOR ISSUES:
Issue:
The collection callback runs before discovered neighbors are enqueued.

Why It Matters:
Saved `pending` state omits devices found during the completed collection, preventing recovery of interrupted traversal.

Recommended Fix:
Emit checkpoint state after discovery/enqueue processing, including queued devices.

DDR REVIEW:
UNCHANGED DD:2026-08-04

OUTSTANDING RISKS:
- Plaintext checkpoint JSON and single-process write assumption remain accepted PoC constraints.

OPEN QUESTIONS:
None.

RECOMMENDED NEXT PHASE:
CheckpointingRemediation