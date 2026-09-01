PHASE:
CommandCollectionTimeoutEvidence

FILES:
app/ssh_client.py
app/collector.py

ACCEPTANCE CRITERIA:
- run_command() returns elapsed_seconds and a distinct error_type ("timeout" | "ssh_exception") for every result.
- On timeout, any stdout/stderr already buffered before the exception is captured instead of discarded as empty strings.
- Device summary records, per failed command: command string, elapsed_seconds, error_type.
- Existing 153 tests continue to pass; no behaviour change for successful commands.

CONSTRAINTS:
- Do not change self.timeout value or add new timeout configuration.
- Do not modify vendor_profiles.py command sets.
- Do not add paging/prompt-detection logic.

KNOWN RISKS:
- paramiko may not expose partial buffered output on all exception paths; evidence capture may be incomplete for some failure modes.
- Adding timing instrumentation has negligible but nonzero per-command overhead.

OUTSTANDING RISKS:
- The command that timed out and its exact device-side cause remain unconfirmed until this phase's evidence is field-tested.

OPEN QUESTIONS:
- Whether the timeout results from command duration, interactive paging, or a generic command-profile mismatch (deferred until evidence collected).
