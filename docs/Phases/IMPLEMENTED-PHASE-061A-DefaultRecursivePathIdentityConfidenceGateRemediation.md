PHASE:
PHASE-061A-DefaultRecursivePathIdentityConfidenceGateRemediation

STATUS:
Implemented

FILES MODIFIED:
- app/orchestrator.py
- tests/test_orchestrator.py

CHANGES:
- In _probe_identity(), when the retain-existing-identity branch is taken (probe confidence <= existing confidence) and device.vendor is "auto" or "unknown", device.vendor is now synchronized to the retained identity's vendor.
- Confidence-gating semantics unchanged: the overwrite branch (probe strictly more confident) is untouched.
- Added test_auto_vendor_synced_when_retaining_higher_confidence_identity, proving vendor="auto" with existing identity confidence 0.95 and a lower-confidence (cisco) probe result in device.vendor == "aruba" and confidence remaining 0.95.

REASON:
- Terra's PHASE-061 review found that a retained higher-confidence identity could coexist with device.vendor="auto", causing execute_device_collection() to still select the generic profile despite valid retained identity metadata. This is the minimal fix: synchronize device.vendor in the retain-existing branch only.

VALIDATION:
- `python -m py_compile app/orchestrator.py tests/test_orchestrator.py` passed.
- `pytest tests/test_orchestrator.py -v` passed (15 tests).
- `pytest` full suite passed (295 tests, 1 pre-existing warning).
- Independent reproducer confirmed: vendor="auto" + existing confidence 0.95 + probe confidence lower resolves device.vendor to the retained vendor without altering confidence.

DDR UPDATES:
UNCHANGED DD:DD-015

RISKS INTRODUCED:
- None beyond PHASE-061's existing known risk (one extra SSH connection per auto/unknown device).

RISKS RESOLVED:
- Devices with vendor="auto"/"unknown" that retain a higher-confidence identity no longer fall back to the generic profile.

OPEN ISSUES:
- The separate "unreachable" field symptom remains out of scope.
