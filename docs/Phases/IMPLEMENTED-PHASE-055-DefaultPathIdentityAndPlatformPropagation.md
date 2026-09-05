PHASE:
DefaultPathIdentityAndPlatformPropagation

STATUS:
Implemented

FILES MODIFIED:
app/parallel_collector.py
- Added identity probe (`show version` via asyncssh) at the start of `_collect_device()`.
- Populated `device.metadata["identity"]` and `device.metadata["role"]` from `identify_device()` and `classify_role()` when the probe succeeds.
- Updated `summary` vendor/platform/model/identity_confidence/role/role_confidence fields from the detected identity.
- Passed resolved `platform` into `get_vendor_commands()` so DD-012's platform-aware profile selection engages on the parallel/recursive/target-device path.
- On probe failure, returned an error bundle rather than falling back to generic commands.

tests/test_parallel_collector.py
- Added `FakeAsyncSSHConnection` and `FakeAsyncSSHConnect` helpers for deterministic asyncssh mocking.
- Added `test_parallel_collect_device_performs_identity_probe`.
- Added `test_parallel_collect_device_selects_aruba_cx_profile` (regression for the reported defect).
- Added `test_parallel_collect_device_probe_failure_is_recorded`.
- Added `test_parallel_collect_device_preserves_pre_populated_identity`.

TESTS ADDED:
- tests/test_parallel_collector.py::test_parallel_collect_device_performs_identity_probe
- tests/test_parallel_collector.py::test_parallel_collect_device_selects_aruba_cx_profile
- tests/test_parallel_collector.py::test_parallel_collect_device_probe_failure_is_recorded
- tests/test_parallel_collector.py::test_parallel_collect_device_preserves_pre_populated_identity

DDR UPDATES:
UNCHANGED DD:[2026-09-04]

RISKS INTRODUCED:
- One additional SSH `show version` round trip per device collected on the parallel path, increasing collection time.
- Detection heuristics remain as accurate/inaccurate as `app/detector.py` already is; no new detection logic was added.

RISKS RESOLVED:
- Default recursive / `--target-device` collection no longer bypasses DD-012 platform-aware profile selection.
- ArubaOS-CX devices reached via the parallel path now select the `aruba-cx` profile instead of the generic profile.
- Generic-profile fallback on the default path is no longer silent for auto-detected devices; probe failure is recorded as an error status.

OPEN ISSUES:
- ArubaOS-CX neighbour discovery parsing remains non-functional (PHASE-058).
- Parallel-path evidence contract still diverges from the sequential path (PHASE-056).
- Partial-status health scoring still unaffected by failed commands (PHASE-057).
