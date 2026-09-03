PHASE:
RecoveredSessionDiagnosticStateRefresh

FILES:
app/ssh_client.py
tests/test_ssh_client.py

ACCEPTANCE CRITERIA:
- Add original_channel_state and original_transport_state fields to the recovery result, preserving the pre-retry snapshot (symmetry with existing original_transport_active).
- Capture retry_channel_state and retry_transport_state reflecting the recovered session immediately after the retry attempt (success or failure).
- On successful recovery, top-level channel_state and transport_state must reflect the recovered session, not the original dead session.
- On failed recovery, top-level channel_state and transport_state remain the original pre-retry snapshot (current behaviour), now also duplicated under original_channel_state/original_transport_state.
- Existing tests/test_cli.py assertions must continue to pass unmodified unless they assert the pre-retry snapshot for a successfully recovered command, in which case update only the specific outdated assertion.

VALIDATION:
- tests/test_ssh_client.py: 8 passed
- Targeted CLI tests: 2 passed
- Full suite: 187 passed

NOTES:
- Updated _try_recover_timeout to store original_channel_state/original_transport_state from the original result, add retry_channel_state/retry_transport_state from the retry result, and refresh top-level channel_state/transport_state when recovery succeeds.
- Added regression tests covering successful recovery, failed retry, and recovery connection failure.
- No changes to timeout values, retry policy, SSH negotiation, vendor detection, provenance, or collector serialization.
