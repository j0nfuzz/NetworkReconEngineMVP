PHASE:
TimeoutDiagnosticEvidenceSerialization

STATUS:
Implemented

FILES MODIFIED:
- app/collector.py
  - command_evidence now includes transport_state and channel_state from ssh_client.run_command() results.
  - Existing evidence fields (transport_active, error_type, recovery_*, original_*, retry_*) remain unchanged.
- tests/test_cli.py
  - Updated test_recovered_command_evidence_includes_failed_retry_attempts to assert transport_state/channel_state propagation.
  - Updated test_end_to_end_timeout_recovery_serializes_evidence to assert transport_state/channel_state survive into summary.json, troubleshooting_bundle.json, and the device ZIP archive.

TESTS ADDED/MODIFIED:
- tests/test_cli.py (2 tests extended)

DDR UPDATES:
UNCHANGED DD:DD-008

RISKS INTRODUCED:
- Slightly larger summary.json/troubleshooting_bundle.json payloads per device.
- For recovered commands, transport_state/channel_state currently reflect the original timeout state because ssh_client.py does not update them after successful retry; this is a known semantic limitation of the existing instrumentation.

RISKS RESOLVED:
- PHASE-036 channel/transport diagnostics now reach field-evidence artefacts for analysis.

OPEN ISSUES:
- Recovered-command state fields may need clarification in a future ssh_client.py refinement phase.
