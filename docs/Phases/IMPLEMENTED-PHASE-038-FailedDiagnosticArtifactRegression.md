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

VALIDATION:
- Targeted tests passed: tests/test_cli.py::test_recovered_command_evidence_includes_failed_retry_attempts, tests/test_cli.py::test_end_to_end_timeout_recovery_serializes_evidence
- Full suite passed: 184 tests in ~18s

NOTES:
- Extended test_recovered_command_evidence_includes_failed_retry_attempts to persist the bundle and assert failed-command diagnostics survive in all artefact outputs.
- No changes to app/ssh_client.py, app/collector.py, timeout/recovery/retry logic, provenance, or vendor behaviour.
