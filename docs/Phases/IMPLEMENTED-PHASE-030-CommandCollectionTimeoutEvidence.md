PHASE:
CommandCollectionTimeoutEvidence

STATUS:
Implemented

FILES MODIFIED:
- app/ssh_client.py
  - Added elapsed_seconds to every run_command() result.
  - Classified failures as error_type "timeout" or "ssh_exception".
  - Captured buffered stdout/stderr before an exception via _read_partial_output().
- app/collector.py
  - Records per-failed-command evidence in summary["failed_command_details"].
  - Preserves partial stdout/stderr in raw_outputs for failed commands.
- tests/test_cli.py
  - Added socket import.
  - Added tests for success timing, timeout classification, SSH exception classification, partial-output preservation, and collector summary evidence.
- docs/PROJECT-JOURNAL.md
  - Appended PHASE-030 journal entry.

TESTS ADDED:
- test_run_command_records_elapsed_seconds_on_success
- test_run_command_classifies_timeout_and_preserves_partial_output
- test_run_command_classifies_ssh_exception
- test_run_command_preserves_partial_stderr_on_ssh_exception
- test_execute_device_collection_records_failed_command_evidence

DDR UPDATES:
UNCHANGED DD:DD-006

RISKS INTRODUCED:
- Summary now includes failed_command_details key; downstream consumers that only inspected summary["failed_commands"] may need updating.
- Partial output capture depends on Paramiko channel buffer state and may be incomplete for some failure modes.

RISKS RESOLVED:
- Collection failures now provide actionable per-command evidence (elapsed time, error type, partial output) for root-cause analysis.

OPEN ISSUES:
- Whether the timeout results from command duration, interactive paging, or a generic command-profile mismatch remains unconfirmed until field evidence is reviewed.
