PHASE:
CommandTimeoutSessionRecovery

FILES:
app/ssh_client.py

ACCEPTANCE CRITERIA:
- run_command() records whether the SSH transport is active (transport.is_active()) at the point of failure.
- On a "timeout" error_type only, exactly one reconnect + single retry of the same command is attempted; no retry occurs for "ssh_exception".
- Result includes recovery_attempted (bool) and recovery_successful (Optional[bool]) fields alongside existing elapsed_seconds/error_type.
- If retry succeeds, the command result reflects success with its own elapsed_seconds; if retry fails, original timeout evidence is preserved plus recovery outcome.
- Existing 160 tests continue to pass; no behaviour change for successful commands or non-timeout failures.

CONSTRAINTS:
- Do not modify self.timeout or add new timeout configuration.
- Do not retry ssh_exception failures.
- Do not add paging/prompt-detection logic.
- Reconnect attempt must be single-shot (no loops, no backoff).

KNOWN RISKS:
- Reconnect may itself raise SSHException/OSError if the underlying transport is unrecoverable; must be caught and recorded, not propagated.
- Retrying a command after reconnect changes device-side session state (new login); acceptable only because it is diagnostic and bounded to one attempt.

OUTSTANDING RISKS:
- Device-side root cause of the initial show version timeout remains unknown (carried from PHASE-032).

OPEN QUESTIONS:
- If recovery succeeds, whether reused-session collection should adopt reconnect-on-timeout by default (deferred to next phase based on this evidence).
