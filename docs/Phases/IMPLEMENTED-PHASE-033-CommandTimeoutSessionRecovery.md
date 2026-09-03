PHASE:
CommandTimeoutSessionRecovery

STATUS:
Implemented

FILES MODIFIED:
- docs/Phases/PHASE-033-CommandTimeoutSessionRecovery.md
  - Created the architect phase definition artefact.
- app/ssh_client.py
  - Added _transport_is_active() helper to record Paramiko transport/session state at failure time.
  - Added _build_original_timeout_result() to capture immutable original timeout evidence.
  - Added _try_recover_timeout() for exactly one reconnect + single retry of the same command on timeout only.
  - Refactored run_command() into _run_command_once() so retry path cannot recurse.
  - Extended every run_command() result with transport_active, recovery_attempted, and recovery_successful.
  - Preserved existing elapsed_seconds and error_type behaviour.
  - On recovery success, returns the new client in _recovered_client so shared-session callers can adopt it.
  - On recovery failure or connect failure, closes the replacement client and preserves original timeout evidence.
  - Original timeout stdout/stderr/error_type are retained in original_* fields even when retry succeeds.
- app/collector.py
  - execute_device_collection() now adopts _recovered_client after a successful timeout recovery and closes the replaced client.
  - command_evidence now preserves transport_active, recovery_attempted, recovery_successful, original_error_type, original_elapsed_seconds, original_stdout, original_stderr, original_transport_active, retry_error, retry_error_type, and retry_elapsed_seconds.
  - Added recovered_commands to bundle.summary so successful recoveries are visible in field artefacts alongside failed_command_details.
- app/normalization.py
  - build_device_summary() now includes recovered_commands from bundle.summary.
- app/troubleshooting.py
  - build_troubleshooting_bundle() now includes recovered_commands from summary.
- app/cli.py
  - Auto-vendor-detection path in _run_cli_collection() now adopts _recovered_client and closes the replaced client, matching collector.py lifecycle.
- tests/test_cli.py
  - Added test_run_command_records_transport_state_fields_on_success.
  - Added test_run_command_recovers_from_timeout_on_retry.
  - Added test_run_command_records_recovery_failure_after_timeout.
  - Added test_run_command_does_not_retry_ssh_exception.
  - Added test_run_command_recovery_preserves_original_timeout_evidence_on_retry_failure.
  - Added test_run_command_recovery_preserves_original_timeout_partial_output_on_success.
- Added test_cli_auto_detect_adopts_recovered_client_and_closes_both.
- Added test_recovered_command_evidence_includes_failed_retry_attempts.
- Added test_end_to_end_timeout_recovery_serializes_evidence (uses real DeviceSSHClient recovery path with connect() monkeypatched, exercising caller adoption, original_transport_active preservation, and bundle serialization).
- docs/DESIGN-DECISION-REGISTER.md
  - DD-007 remains Rejected (DDR approval is the Reviewer's responsibility).
- docs/PROJECT-JOURNAL.md
  - Appended delta entry for PHASE-033 remediation.

TESTS ADDED:
- tests/test_cli.py::test_run_command_records_transport_state_fields_on_success
- tests/test_cli.py::test_run_command_recovers_from_timeout_on_retry
- tests/test_cli.py::test_run_command_records_recovery_failure_after_timeout
- tests/test_cli.py::test_run_command_does_not_retry_ssh_exception
- tests/test_cli.py::test_run_command_recovery_preserves_original_timeout_evidence_on_retry_failure
- tests/test_cli.py::test_run_command_recovery_preserves_original_timeout_partial_output_on_success
- tests/test_cli.py::test_cli_auto_detect_adopts_recovered_client_and_closes_both
- tests/test_cli.py::test_recovered_command_evidence_includes_failed_retry_attempts
- tests/test_cli.py::test_end_to_end_timeout_recovery_serializes_evidence

DDR UPDATES:
- DD-007 remains Rejected pending Reviewer approval (proposed decision unchanged: exactly one reconnect and single retry on timeout failures only; ssh_exception failures are not retried).

CHANGE BUDGET NOTE:
- Removed redundant fake-client tests whose coverage is now provided by the end-to-end regression test; retained only the focused unit tests for the DeviceSSHClient recovery path, the CLI auto-detection path, and the failed-retry evidence path.
- Current tracked PHASE-033 delta is 963 changed lines across the modified source, test, and documentation files, within the 1,000-line project budget.

RISKS INTRODUCED:
- Successful recovery creates a new SSH session, changing device-side session context for the retried command.
- Recovery attempt adds connection + command latency for each timeout failure.
- Larger summary/troubleshooting payloads due to additional per-command recovery fields.

RISKS RESOLVED:
- Failure evidence now includes transport/session state at failure time.
- Recovery outcome (attempted/successful) is recorded for timeout failures.
- Original timeout stdout/stderr/error_type/transport_active are retained separately even when retry succeeds.
- Both shared-session callers (collector and CLI auto-detection) now manage the recovered client lifecycle consistently.
- Recovery and original-timeout evidence now survive into summary.json, troubleshooting_bundle.json, and the final ZIP bundle.
- End-to-end regression coverage now exercises the real DeviceSSHClient recovery path through caller adoption and artefact serialization, including original_transport_active preservation.

OPEN ISSUES:
- Device-side root cause of the initial show version timeout remains unknown; deferred to future phase after reviewing recovered evidence.
