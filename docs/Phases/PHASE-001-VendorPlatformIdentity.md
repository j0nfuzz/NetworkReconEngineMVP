PHASE:
Vendor/Platform Identity Detection (PoC)

FILES:
- app/models.py
- app/detector.py
- app/cli.py
- app/collector.py
- tests/test_detector.py

ACCEPTANCE CRITERIA:
- DeviceIdentity{vendor, platform, model, confidence} returned by identify_device(raw_text)
- Falls back to vendor="generic", platform="unknown", model="unknown" on no match
- cli.py consumes identify_device() output
- device.vendor remains backwards compatible
- summary.json gains vendor/platform/model fields
- Tests cover cisco, aruba, juniper and unknown
- No regressions

CONSTRAINTS:
- No new SSH commands
- No changes to vendor_profiles command sets
- Maintain backwards compatibility

KNOWN RISKS:
- Regex detection may fail on real-world output
- Platform heuristics unproven

OUTSTANDING RISKS:
- No real device sample corpus
- Confidence scoring unvalidated

OPEN QUESTIONS:
- Platform/model influence deferred?
- Identity object vs summary fields?