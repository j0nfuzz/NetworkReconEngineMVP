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

CONSTRAINTS:
- Do not change timeout thresholds, retry count, or the timeout-only recovery policy (DD-007).
- Do not modify provenance capture (DD-008).
- Do not modify vendor detection, SSH negotiation, or collector serialization logic (app/collector.py untouched).
- Single reconnect/retry attempt only; no additional retries.

KNOWN RISKS:
- Slightly larger result payload per recovered command.
- If tests/test_cli.py contains an assertion tied to old pre-retry semantics for a successful recovery, it must be identified and corrected as part of this phase.

OUTSTANDING RISKS:
- Diagnostic semantics require fresh field evidence to confirm real-device behaviour matches synthetic test expectations (carried from PHASE-037 review).

OPEN QUESTIONS:
- None.
