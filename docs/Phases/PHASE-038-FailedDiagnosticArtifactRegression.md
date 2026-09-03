PHASE:
FailedDiagnosticArtifactRegression

FILES:
tests/test_cli.py

ACCEPTANCE CRITERIA:
- Extend or add a test where a failed command with recovery_attempted=True carries channel_state and transport_state through execute_device_collection() and write_bundle().
- Assert channel_state and transport_state are present on the failed_command_details entry in summary.json.
- Assert the same fields are present in troubleshooting_bundle.json.
- Assert the same fields are present in the device ZIP archive's summary.json and troubleshooting_bundle.json.
- No production code changes required or permitted.

CONSTRAINTS:
- Do not modify app/collector.py.
- Do not modify app/ssh_client.py.
- Do not modify timeout, recovery, retry, negotiation, or vendor detection behaviour.
- Do not modify provenance capture (DD-008).

KNOWN RISKS:
- None; this is a test-only regression addition.

OUTSTANDING RISKS:
- None.

OPEN QUESTIONS:
- None.
