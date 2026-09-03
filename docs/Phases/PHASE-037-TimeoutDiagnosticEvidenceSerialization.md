PHASE:
TimeoutDiagnosticEvidenceSerialization

FILES:
app/collector.py
tests/test_cli.py

ACCEPTANCE CRITERIA:
- command_evidence in execute_device_collection() includes channel_state and transport_state sourced from ssh_client.run_command() results.
- summary.json, troubleshooting_bundle.json, and the device ZIP archive all carry channel_state/transport_state for failed_command_details and recovered_commands entries.
- Existing evidence fields (transport_active, error_type, recovery_attempted, recovery_successful, original_*, retry_*) remain unchanged and are not renamed or removed.

CONSTRAINTS:
- Do not modify app/ssh_client.py.
- Do not modify timeout, recovery, retry, or SSH negotiation behaviour (DD-007).
- Do not modify provenance capture (DD-008).
- No vendor profile or paging changes.

KNOWN RISKS:
- Larger summary.json/troubleshooting_bundle.json payloads per device.

OUTSTANDING RISKS:
- PHASE-036 diagnostics remain unvalidated against real field data until a fresh bundle is captured against the legacy device.

OPEN QUESTIONS:
- None.
