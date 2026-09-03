# PHASE-034 Field Evidence Findings

## Collection Metadata

- Phase: PHASE-034-FieldEvidenceCaptureAndAnalysisPostRecovery
- Build: uncommitted PHASE-033 working tree containing DD-007 recovery instrumentation
- Base commit: `0c0023ff8f75c89d4ea320c2f44e94a5c6250570` (PHASE-031: preserve command failure evidence in bundles)
- Working-tree diff fingerprint (SHA-1 of `git diff --binary` over tracked files): `04a07b238b18b66bfaf4c54ecde17f66464f9aef`
- Reproduction procedure (run from repository root):
  1. Check out the base commit:
     ```text
     git checkout 0c0023ff8f75c89d4ea320c2f44e94a5c6250570
     ```
  2. Apply the exact uncommitted PHASE-033 working-tree diff. A reviewer can obtain this diff by checking out the original collection state (or a state with identical tracked-file changes) and running:
     ```text
     git diff --binary > phase-034-build.patch
     sha1sum phase-034-build.patch  # must equal 04a07b238b18b66bfaf4c54ecde17f66464f9aef
     git apply phase-034-build.patch
     ```
  3. Run the collection using the legacy dependency profile:
     ```text
     .\.venv-legacy\Scripts\python.exe -m app.cli --config config/interactive_devices.yml --output-dir output/PHASE-034 --verbose
     ```
- Required dependency profile: legacy (`requirements-legacy.txt`, `paramiko==2.12.0`)
- Source files modified in the working-tree delta:
  - `app/cli.py`, `app/collector.py`, `app/normalization.py`, `app/ssh_client.py`, `app/troubleshooting.py`
  - `docs/DESIGN-DECISION-REGISTER.md` (DD-007 added, status `Approved`)
  - `docs/PROJECT-JOURNAL.md`
  - `tests/test_cli.py`, `tests/test_normalization.py`, `tests/test_troubleshooting.py`
- Diff stat: 10 files changed, 999 insertions(+), 17 deletions(-)
- Bundle generated: 2026-09-02T15:33:34.959221+00:00
- Bundle directory: output/PHASE-034/interactive-device
- Bundle artefact hashes (SHA-256):
  - `interactive-device.zip`: `aaf0ff2869f1c713a9bc0b50eaaef8c6feed065e3732489fe81566fff579017b`
  - `summary.json`: `99135d98e52622aed4e030ca1ca657ad912bf1e778e21eea0c0af1db50954a67`
  - `troubleshooting_bundle.json`: `caf834cea8f7607b801225aa53ed31857cc428c87424e5a15b64393dd5374430`
- Device label: interactive-device
- Hostname: <REDACTED>
- Collection mode: live (dry_run: false)
- Dependency profile: legacy (paramiko==2.12.0)
- Total commands run: 5
- Collection status: partial

## Recovered Commands

```json
[]
```

No commands were successfully recovered in this capture.

## Failed Command Details

Verbatim extract from `summary.json` / `troubleshooting_bundle.json`:

```json
[
  {
    "command": "show version",
    "elapsed_seconds": 15.07210219999979,
    "error_type": "timeout",
    "transport_active": true,
    "recovery_attempted": true,
    "recovery_successful": false,
    "original_error_type": "timeout",
    "original_elapsed_seconds": 15.07210219999979,
    "original_stdout": "",
    "original_stderr": "",
    "original_transport_active": true,
    "retry_error": "Command timed out or failed: ",
    "retry_error_type": "timeout",
    "retry_elapsed_seconds": 15.090014699999301
  },
  {
    "command": "show interfaces",
    "elapsed_seconds": 0.040328900000531576,
    "error_type": "ssh_exception",
    "transport_active": false,
    "recovery_attempted": false,
    "recovery_successful": null,
    "original_error_type": null,
    "original_elapsed_seconds": null,
    "original_stdout": null,
    "original_stderr": null,
    "original_transport_active": null,
    "retry_error": null,
    "retry_error_type": null,
    "retry_elapsed_seconds": null
  },
  {
    "command": "show ip route",
    "elapsed_seconds": 4.499999704421498e-06,
    "error_type": "ssh_exception",
    "transport_active": false,
    "recovery_attempted": false,
    "recovery_successful": null,
    "original_error_type": null,
    "original_elapsed_seconds": null,
    "original_stdout": null,
    "original_stderr": null,
    "original_transport_active": null,
    "retry_error": null,
    "retry_error_type": null,
    "retry_elapsed_seconds": null
  },
  {
    "command": "show arp",
    "elapsed_seconds": 1.2000000424450263e-06,
    "error_type": "ssh_exception",
    "transport_active": false,
    "recovery_attempted": false,
    "recovery_successful": null,
    "original_error_type": null,
    "original_elapsed_seconds": null,
    "original_stdout": null,
    "original_stderr": null,
    "original_transport_active": null,
    "retry_error": null,
    "retry_error_type": null,
    "retry_elapsed_seconds": null
  },
  {
    "command": "show system uptime",
    "elapsed_seconds": 8.000006346264854e-07,
    "error_type": "ssh_exception",
    "transport_active": false,
    "recovery_attempted": false,
    "recovery_successful": null,
    "original_error_type": null,
    "original_elapsed_seconds": null,
    "original_stdout": null,
    "original_stderr": null,
    "original_transport_active": null,
    "retry_error": null,
    "retry_error_type": null,
    "retry_elapsed_seconds": null
  }
]
```

## Recovery Evidence Summary

| Command | elapsed_seconds | error_type | transport_active | original_transport_active | recovery_attempted | recovery_successful |
|---|---|---|---|---|---|---|
| show version | 15.0721022 | timeout | true | true | true | false |
| show interfaces | 0.0403289 | ssh_exception | false | null | false | null |
| show ip route | 0.0000045 | ssh_exception | false | null | false | null |
| show arp | 0.0000012 | ssh_exception | false | null | false | null |
| show system uptime | 0.0000008 | ssh_exception | false | null | false | null |

## Artefact Verification

- `summary.json` contains `failed_commands`, `failed_command_details`, and `recovered_commands`.
- `troubleshooting_bundle.json` contains the same recovery evidence fields.
- The zipped device archive retains both JSON artefacts and the per-command text files unchanged.
- Recovery evidence fields are present verbatim as required by DD-007.

## Observations (Evidence Only)

1. `show version` raised a timeout after approximately 15 seconds while `original_transport_active` was `true`.
2. DD-007 recovery was attempted for `show version`: a new SSH connection was established and the command was retried once without recovery.
3. The retry of `show version` also timed out after approximately 15 seconds (`retry_elapsed_seconds`: 15.09).
4. Because recovery failed, the collector retained the original client; the original transport subsequently reported `transport_active: false` on the next command.
5. All subsequent commands (`show interfaces`, `show ip route`, `show arp`, `show system uptime`) failed with `error_type: ssh_exception` and `transport_active: false`.
6. No partial stdout or stderr was captured for any failed command.
7. No pager markers (`--More--`, `more`, `press any key`, etc.) were observed.

## Findings (Evidence Only)

The observations are stated below without inferring causation.

### 1. Session death at the original timeout

`show version` timed out while `original_transport_active` was `true`.

Per the PHASE-034 acceptance criterion, `transport_active: true` at the original timeout **disproves** session death at that instant.

**Conclusion: Session death at the original timeout is DISPROVEN.**

### 2. Session death after the original timeout

After the `show version` timeout and the failed DD-007 recovery retry, every subsequent command failed with `error_type: ssh_exception` and `transport_active: false`.

The transport state transitioned from active at timeout to inactive before the next command.

**Conclusion: Session death after the original timeout is SUPPORTED by the evidence.**

### 3. Whether the timeout caused session death

The evidence shows:
- active transport at timeout,
- inactive transport on subsequent commands,
- no recovered session,
- no partial output or pager markers.

This sequence is consistent with the timeout-kills-session hypothesis, but it does not establish causation. The session may have become inactive during the timeout wait, during the recovery reconnect, or for an unrelated device-side reason.

**Conclusion: Causation remains INCONCLUSIVE.**

### Summary Classification

| Hypothesis | Evidence Verdict |
|---|---|
| Session was already dead at the original timeout | Disproven |
| Session died after the original timeout | Supported |
| The timeout event caused the session death | Inconclusive |

## Redactions

- Device hostname, IP address, username, password, and any device-specific command output have been omitted or replaced with placeholders.
- Only failure metadata, recovery evidence, and artefact structure are recorded above.
