# PHASE-032 Field Evidence Findings

## Collection Metadata

- Phase: PHASE-032-FieldEvidenceCaptureAndAnalysis
- Build commit: 9e8827c (PHASE-031 approved)
- Bundle generated: 2026-09-02T13:29:29Z
- Device label: <FIELD_DEVICE>
- Collection mode: live (dry_run: false)
- Total commands run: 5
- Collection status: partial

## Failed Commands Summary

| Command | elapsed_seconds | error_type | Partial Output | First Line |
|---|---|---|---|---|
| show version | 15.086462700000084 | timeout | 58 bytes, 5 lines | `ERROR: Command timed out or failed:` |
| show interfaces | 0.046127800000022035 | ssh_exception | 58 bytes, 5 lines | `ERROR: Command timed out or failed:` |
| show ip route | 0.000004499999931795173 | ssh_exception | 80 bytes, 5 lines | `ERROR: Command timed out or failed: SSH session not active` |
| show arp | 0.0000013999999737279722 | ssh_exception | 80 bytes, 5 lines | `ERROR: Command timed out or failed: SSH session not active` |
| show system uptime | 0.0000010000001111620804 | ssh_exception | 80 bytes, 5 lines | `ERROR: Command timed out or failed: SSH session not active` |

## Raw Evidence Notes

- No partial stdout or stderr was captured for any failed command.
- No pager markers (`--More--`, `more`, `press any key`, etc.) were observed.
- No prompt terminators (`>` or `#` at line end) were observed.
- The first command, `show version`, exceeded the configured timeout threshold before returning.
- Subsequent commands failed rapidly with `error_type: ssh_exception` and an inactive-session indicator.

## Artefact Verification

- `summary.json` contains `failed_commands` and `failed_command_details` with `elapsed_seconds` and `error_type`.
- `troubleshooting_bundle.json` contains the same `failed_commands` and `failed_command_details`.
- The zipped device archive retains both JSON artefacts and the per-command text files unchanged.

## Observations (Evidence Only)

- The failure pattern is sequential: one timeout followed by cascading inactive-session exceptions.
- `show version` is not exempt from the timeout behaviour in this capture; it also returned `error_type: timeout`.
- All four commands previously reported as failing are represented in the evidence; no new failing commands were introduced.

## Redactions

- Device hostname, IP address, username, password, and any device-specific command output have been omitted.
- Only failure metadata and artefact structure are recorded above.
