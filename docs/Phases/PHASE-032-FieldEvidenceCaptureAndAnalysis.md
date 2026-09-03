PHASE:
FieldEvidenceCaptureAndAnalysis

FILES:
docs/Phases/PHASE-032-FieldEvidenceCaptureAndAnalysis.md
docs/FieldEvidence/PHASE-032-<timestamp>-bundle-findings.md

ACCEPTANCE CRITERIA:
- One field bundle collected using the PHASE-031-approved build (commit 9e8827c or later).
- failed_command_details extracted for all four failing commands: show interfaces, show ip route, show arp, show system uptime.
- Each command's elapsed_seconds and error_type recorded verbatim from the bundle.
- Any captured partial stdout/stderr documented per command.
- Findings written to a field-evidence report; no source code modified.

CONSTRAINTS:
- Do not modify app/ssh_client.py, app/collector.py, vendor_profiles, or any timeout/paging/prompt logic.
- Do not perform speculative remediation based on findings; capture and report only.
- Bundle must be generated after commit 9e8827c to guarantee instrumentation is present.

KNOWN RISKS:
- Field device may not be reachable during the session, delaying evidence capture.
- Partial output may still be empty for some error_type values (paramiko buffer limitation, carried from PHASE-030).

OUTSTANDING RISKS:
- Root cause of the four command failures remains unknown until this phase completes.

OPEN QUESTIONS:
- Whether failures share one error_type (suggesting a single triggering event) or differ per command.
