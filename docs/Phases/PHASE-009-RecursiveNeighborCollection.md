PHASE:
Recursive Neighbor Collection

FILES:
- app/orchestrator.py (new)
- tests/test_orchestrator.py (new)

ACCEPTANCE CRITERIA:
- New function (e.g. `run_recursive_collection(seed_device, default_credentials)`) drives collection starting from a single seed Device.
- After collecting a device via existing `execute_device_collection()`, its `discovered_neighbors` are passed through existing `classify_neighbors()`.
- Only neighbors classified as a supported vendor are enqueued for collection; unsupported/unknown neighbors are recorded (name + classification) but not connected to.
- Neighbors lacking an IP address are recorded as failed/skipped, not queued (no hostname to connect to).
- Visited devices are never re-queued or re-collected (cycle prevention), reusing the visited/pending/failed/successful vocabulary established in PHASE-006A.
- Devices constructed for discovered neighbors use `default_credentials` (from PHASE-008 default block) for username/password/enable_password; no per-neighbor credential entries exist since neighbors are undiscovered until runtime.
- Function returns a structured result: `{"successful": [...], "failed": [...], "unsupported": [...], "bundles": {name: DeviceBundle}}`.
- Tests cover: seed-only run (no neighbors), supported neighbor enqueued and collected, unsupported neighbor recorded but not connected, already-visited neighbor not re-queued, neighbor missing IP address skipped.

CONSTRAINTS:
- No new dependencies (reuse paramiko/yaml already in use).
- No concurrency/asyncio (Wishlist Phase 9, out of scope).
- No checkpoint persistence (Wishlist Phase 10, out of scope).
- No encrypted credential storage/vault (explicitly deferred).
- No changes to execute_device_collection(), classify_neighbors(), traverse_topology(), or load_devices() signatures — orchestrator composes existing functions only.
- No changes to Device dataclass fields.

KNOWN RISKS:
- None beyond those already carried.

OUTSTANDING RISKS:
- Neighbor records may lack an IP in some vendor outputs, limiting how many discovered devices can actually be collected (carried forward from PHASE-007).
- Plaintext default credentials applied to all discovered neighbors assume homogeneous credentials across the environment (accepted PoC limitation per Wishlist Phase 8 "Future" section).

OPEN QUESTIONS:
- None.
