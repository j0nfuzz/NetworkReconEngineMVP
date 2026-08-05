PHASE:
PHASE-012-DataNormalisation

STATUS:
Implemented

FILES MODIFIED:
- app/normalization.py (new)
  - Added `build_device_summary(bundle: DeviceBundle) -> dict`.
  - Produces deterministic vendor-independent summary structure: hostname, vendor, model, version, uptime_days, cpu, memory, routes, arp_entries, interface_errors.
  - Cisco-specific regex/keyword parsers for version, model, uptime, cpu, memory, routes, arp, and interface errors.
  - Safe defaults when values unavailable; function never raises.
  - Raw `bundle.raw_outputs` and `bundle.summary` are consumed read-only.
- tests/test_normalization.py (new)
  - Added full Cisco summary test.
  - Added missing-value defaults test.
  - Added deterministic output shape test.
  - Added unknown vendor defaults test.
  - Added no-mutation-of-bundle test.

TESTS ADDED:
- tests/test_normalization.py::test_build_device_summary_full_cisco_output
- tests/test_normalization.py::test_build_device_summary_missing_values_use_defaults
- tests/test_normalization.py::test_build_device_summary_deterministic_shape
- tests/test_normalization.py::test_build_device_summary_unknown_vendor_defaults
- tests/test_normalization.py::test_build_device_summary_does_not_mutate_bundle

DDR UPDATES:
UNCHANGED DD:2026-08-04

RISKS INTRODUCED:
- Cisco output format drift may cause silent default values; acceptable for PoC.
- Other vendors return all defaults until vendor-specific parsers are added in future phases.

RISKS RESOLVED:
- None.

OPEN ISSUES:
- None.
