PHASE:
FieldEvidenceCaptureAndAnalysisPostRecovery

FILES:
docs/Phases/PHASE-034-FieldEvidenceCaptureAndAnalysisPostRecovery.md
docs/FieldEvidence/PHASE-034-<timestamp>-bundle-findings.md

ACCEPTANCE CRITERIA:
- One field bundle collected using the PHASE-033-approved build (DD-007 Approved).
- recovered_commands and failed_command_details extracted verbatim for every command against the PHASE-032-affected device.
- transport_active, original_transport_active, recovery_attempted, recovery_successful documented per command.
- Findings state whether transport_active was False at the original timeout (proving session death) or True (disproving it).
- Findings written to a field-evidence report; no source code modified.

CONSTRAINTS:
- Do not modify app/ssh_client.py, app/collector.py, vendor_profiles, or any timeout/paging/prompt logic.
- Do not perform speculative remediation based on findings; capture and report only.
- Bundle must be generated using the DD-007-approved build to guarantee recovery instrumentation is present.

KNOWN RISKS:
- Field device may not be reachable during the session, delaying evidence capture.
- Recovery reconnect may itself fail (ssh_exception), which is itself informative evidence, not a blocker.

OUTSTANDING RISKS:
- Device-side root cause of the initial show version timeout remains unknown (carried from PHASE-032/DD-007).

OPEN QUESTIONS:
- Whether transport_active=False at timeout is sufficient proof of session death, or whether ssh_exception on subsequent commands is required corroboration.
