PHASE:
Role Detection Remediation (PoC)

FILES:
- app/cli.py
- tests/test_cli.py

ACCEPTANCE CRITERIA:
- classify_role() is invoked for every device, not only vendor="auto"
- Configured-vendor devices receive device.metadata["role"] using device.vendor and device.name (no new SSH probe)
- Auto-detected devices retain existing identity-based classification behaviour
- summary.json role/role_confidence reflect classification for both paths
- Test coverage added for a configured-vendor device path
- No regressions

CONSTRAINTS:
- No new SSH commands (reuse configured device.vendor; do not probe for model)
- No changes to classify_role() heuristics (DD-002 logic unchanged)
- Maintain backwards compatibility

KNOWN RISKS:
- Configured-vendor devices lack a model value, reducing classification confidence for model-based rules

OUTSTANDING RISKS:
- Hostname/model heuristics and confidence scoring remain unvalidated against real devices (carried from PHASE-002)

OPEN QUESTIONS:
- None.
