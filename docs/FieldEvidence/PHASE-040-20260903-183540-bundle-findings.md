# PHASE-040 Field Evidence Findings

## Collection Metadata

- Phase: PHASE-040-FieldEvidencePostDiagnosticRefresh
- Build commit: 7abcc4e28e7bd4a871289f36ab969e164fe30514
- Working tree state: dirty
- Patch checksum (SHA-256): b1bcd2a7a7b914a2230263e070c2ece2fcc40a203a4d2c0f839854a6514efb4c
- Bundle generated: 2026-09-03T18:35:40.849313+00:00
- Device labels: sample-cisco-router, sample-juniper-router, sample-aruba-switch
- Collection mode: live (dry_run: false)
- Total commands run: 0
- Collection status: no reachable devices

## Reproduction Command

```powershell
.\.venv\Scripts\python.exe -m app.cli --config config\devices.yml --output-dir field_output_040 --verbose
```

## Reachability Summary

| Device | Hostname | Status | error |
|---|---|---|---|
| sample-cisco-router | 192.168.2.1 | unreachable | timed out |
| sample-juniper-router | 192.168.2.2 | unreachable | timed out |
| sample-aruba-switch | 192.168.2.3 | unreachable | timed out |

## Failed Commands Summary

No commands were executed because all configured devices failed to establish an SSH session. Therefore no timeout, retry, or recovery events were observed.

## Raw Evidence Notes

- No partial stdout or stderr was captured for any command.
- No pager markers were observed.
- No prompt terminators were observed.
- No channel_state or transport_state diagnostics were produced at the command level because the SSH transport never reached the command-execution stage.

## Artefact Verification

- `field_output_040/bundle_manifest.json` exists and records all three devices with status `unreachable`.
- Each device directory contains:
  - `summary.json`
  - `troubleshooting_bundle.json`
  - `ai_prompt.txt`
  - `build_provenance.json`
- `build_provenance.json` exists for each device and records:
  - `head_commit_sha`: `7abcc4e28e7bd4a871289f36ab969e164fe30514`
  - `dirty`: `true`
  - `patch`: working-tree diff relative to HEAD
  - `patch_checksum`: `b1bcd2a7a7b914a2230263e070c2ece2fcc40a203a4d2c0f839854a6514efb4c`
  - `excluded_paths`: `config/*.yml`

## Observations (Evidence Only)

- The configured sample devices (192.168.2.1, 192.168.2.2, 192.168.2.3) were not reachable from the collection host.
- No timeout-then-cascade pattern was observed because no SSH session was established.
- No recovery events occurred because no commands were attempted.
- Provenance instrumentation (DD-008) functioned correctly: HEAD SHA, dirty state, patch, and checksum were recorded despite zero successful commands.

## Redactions

- Device hostnames, usernames, passwords, and any command output have been omitted or were never collected.
- Only reachability metadata and artefact structure are recorded above.

## Assessment of DD-007

DD-007 (timeout-only, single-retry recovery policy) is **inconclusive** based on this evidence.

Reason: the absence of reachable devices means no timeout event, no retry event, and no recovery event were observed. Without such events, the behaviour of the single-retry recovery policy on real hardware cannot be confirmed, contradicted, or characterised.

This outcome matches the known risk documented in PHASE-040: "Lab/field devices may not currently reproduce the original timeout-cascade conditions, yielding inconclusive evidence."

## Conclusion

PHASE-040 collection was executed successfully but produced no timeout/recovery field evidence because the configured target devices were unreachable. The instrumentation chain (diagnostic capture, serialization, provenance) operated correctly and produced the expected artefacts. A fresh field bundle with timeout/recovery events will require either:

- a reachable lab or field device added to `config/devices.yml`, or
- explicit authorization to use the existing `config/interactive_devices.yml` target.

Until such evidence is available, DD-007 remains approved and inconclusively validated by real hardware.
