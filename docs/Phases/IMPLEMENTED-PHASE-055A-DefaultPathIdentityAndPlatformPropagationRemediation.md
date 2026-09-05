PHASE:
DefaultPathIdentityAndPlatformPropagationRemediation

STATUS:
Implemented

FILES MODIFIED:
app/parallel_collector.py
- `_collect_device()` now confidence-gates the vendor/identity overwrite.
  - The probe's `identify_device()` result is compared against any pre-populated
    identity confidence in `device.metadata["identity"]`.
  - The probe only overwrites `device.vendor` and metadata when its confidence
    is strictly greater than the existing confidence; otherwise the configured
    or pre-populated vendor/platform/role are preserved.
  - An unrecognized/ambiguous banner (probe confidence `0`) no longer replaces
    a configured vendor with `generic`.
- The identity probe and command collection now share a single asyncssh
  session.
- The probe's `show version` output is reused as the profile's
  `show version` evidence; the command is skipped in the collection loop to
  prevent executing it twice.
- `get_vendor_commands()` is still called with the resolved `role` and
  `platform` so DD-012 platform-aware selection continues to engage for
  positively-detected devices.

tests/test_parallel_collector.py
- Restored from a single collapsed physical line to valid, newline-delimited,
  importable source; `python -m py_compile tests/test_parallel_collector.py`
  succeeds.
- Updated `test_parallel_collect_device_preserves_pre_populated_identity` to
  assert that a higher-confidence pre-populated identity is preserved when the
  probe is ambiguous.
- Added `test_parallel_collect_device_preserves_configured_vendor_on_ambiguous_probe`:
  a device configured as `cisco` with an unrecognized `show version` banner
  keeps the Cisco vendor/profile and does not fall back to generic commands.
- Added `test_parallel_collect_device_reuses_show_version_output`: the probe's
  `show version` output is recorded in `raw_outputs` and `show version` is only
  executed once.

TESTS ADDED OR UPDATED:
- tests/test_parallel_collector.py::test_parallel_collect_device_performs_identity_probe (retained)
- tests/test_parallel_collector.py::test_parallel_collect_device_selects_aruba_cx_profile (retained)
- tests/test_parallel_collector.py::test_parallel_collect_device_probe_failure_is_recorded (retained)
- tests/test_parallel_collector.py::test_parallel_collect_device_preserves_pre_populated_identity (updated)
- tests/test_parallel_collector.py::test_parallel_collect_device_preserves_configured_vendor_on_ambiguous_probe (new)
- tests/test_parallel_collect_device_reuses_show_version_output (new)

DDR UPDATES:
UNCHANGED DD:[2026-09-04]

VALIDATION RESULTS:
- `python -m py_compile app/parallel_collector.py tests/test_parallel_collector.py` → success
- `python -m pytest tests/test_parallel_collector.py -q` → 23 passed
- `python -m pytest tests -q` → 277 passed, 1 warning

REVIEWER FINDINGS ADDRESSED:
1. Generic-overwrite regression: probe results now only overwrite when they
   have positive confidence and strictly exceed existing identity confidence.
   An unrecognized banner keeps the configured/pre-populated vendor.
2. Duplicate `show version` behaviour: the probe and collection share one SSH
   session and the probe's `show version` output is reused as profile evidence.
3. Validation blocked: `tests/test_parallel_collector.py` is restored to valid
   source and the full suite passes.

RISKS INTRODUCED:
- Single-session collection means a session failure after the probe is recorded
  as `unreachable` with whatever partial outputs were gathered; this matches the
  existing partial-evidence contract.
- Confidence comparison depends on `identify_device()` returning `confidence=0`
  for unrecognized output; if future detector changes alter the baseline, the
  gating logic must be reviewed.

RISKS RESOLVED:
- Configured/discovered vendors are no longer silently downgraded to `generic`
  by an ambiguous probe result.
- Positively-detected devices (e.g. ArubaOS-CX) still receive their platform-
  aware profile on the parallel/recursive/`--target-device` path.
- The extra `show version` round trip per device is eliminated.

RESIDUAL RISKS:
- ArubaOS-CX neighbour discovery remains non-functional regardless of this fix
  (tracked in PHASE-058).
- Parallel-path evidence-contract divergence from the sequential path remains
  open (tracked in PHASE-056).
- Partial-status health scoring remains unaffected by failed commands
  (tracked in PHASE-057).
