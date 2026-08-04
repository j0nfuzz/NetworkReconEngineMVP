PHASE: PHASE-001-VendorPlatformIdentity

STATUS:
Implemented

FILES MODIFIED:
- app/collector.py
  - summary.json now always includes platform, model, and identity_confidence fields.
- app/detector.py
  - Cisco model extraction prefers explicit "Model Number" lines.
  - Aruba model extraction strips trailing parentheses.
  - Arista DCS model pattern captures the full model string.
- tests/test_detector.py
  - New test file (created).

TESTS ADDED:
- tests/test_detector.py
  - identify_device() happy path for cisco, aruba, juniper, arista
  - Unknown fallback returns DeviceIdentity defaults
  - Empty input returns DeviceIdentity defaults
  - detect_vendor_from_show_version() backward compatibility

DDR UPDATES:
UNCHANGED DD:[No entries present]

RISKS INTRODUCED:
- None.

RISKS RESOLVED:
- Missing detector unit tests.
- Summary fields were conditional on metadata identity.
- Regex model extraction produced unstable results for Cisco and Arista.

OPEN ISSUES:
- Confidence scoring remains unvalidated against real device output.
- Platform/model extraction heuristics may need refinement with real-world samples.
