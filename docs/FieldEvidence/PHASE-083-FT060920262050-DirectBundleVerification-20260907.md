# FT060920262050.zip — Direct Bundle Verification (2026-09-07)

Evidence-first re-analysis performed by directly extracting `field_tests/FT060920262050.zip` and reading its contents (this document supersedes the prior "evidence rejection" note, which incorrectly claimed the bundle could not be located).

## Bundle Contents (directly observed)

- Archive: `field_tests/FT060920262050.zip`, 10,962,041 bytes, SHA-256 `184DB0CEA2E2C65C6BED3ECCC08827F0473DA1676BB93953311E618DBAF24DC7`.
- Exactly **two** device folders exist: `192.168.2.241` (seed) and `HOSTNAME-06`. Confirmed via `bundle_manifest.json` (`"name"` appears exactly twice: `192.168.2.241`, `HOSTNAME-06`), `console.log`, and `topology.json` (exactly two `nodes`).
- **No `HOSTNAME-05` device folder, console line, manifest entry, or topology node exists anywhere in this bundle.** The "SW3 candidate: `[verbose] Finished collection for HOSTNAME-05: collected`" line supplied in the request text does not appear in the actual bundle's `console.log`. This is a factual discrepancy in the submitted evidence text, not a bundle finding.
- Both `192.168.2.241/build_provenance.json` and `HOSTNAME-06/build_provenance.json` record identical provenance: `head_commit_sha: c290677ed6cb63170ad36440ef541de7f5ede836`, `dirty: false`.

## Direct Code-State Verification (not documentary inference)

`git show c290677ed6cb63170ad36440ef541de7f5ede836:app/orchestrator.py` shows the identity-probe gate as:
```
if device.vendor in ("auto", "unknown"):
```
with no extension for classification-derived neighbours.

Current HEAD (`5fe7004c713bd5b9eef9cb9726e78aed829597f7`) `app/orchestrator.py` contains an additional gate:
```
discovered_neighbor = bool(device.metadata.get("discovered_neighbor"))
... discovered_neighbor and _existing_identity_confidence(device) <= 0
```

This proves, by direct commit inspection rather than journal narrative, that the code which produced this bundle (c290677) predates the fix present at current HEAD.

## Evidence Chain for HOSTNAME-06

1. `console.log`: seed shows `probing identity...` / `identity resolved: vendor=aruba` before connecting. **HOSTNAME-06 shows no such lines** — only `probing SSH reachability...` / `probe: reachable` / `connecting...`. The identity probe never ran for this device.
2. `HOSTNAME-06/summary.json`: `platform: "unknown"`, `identity_confidence: 0.0`, `commands_run: 13` (the generic/AOS-Switch profile length), `discovered_neighbors: []`.
3. `HOSTNAME-06/show_version.txt` (one of the 13 executed commands) **succeeds** and returns:
   ```
   ArubaOS-CX
   (c) Copyright 2017-2023 Hewlett Packard Enterprise Development LP
   Version : PL.10.11.1021
   ```
   proving the device unambiguously self-identifies as ArubaOS-CX in its own command output.
4. `HOSTNAME-06/show_inventory.txt` = `Invalid input: inventory`; `show_interfaces_brief.txt` = `Invalid input: neighbors` (LLDP file) — confirming AOS-Switch-only verbs were sent to CX hardware and rejected. All 6 `failed_commands` are AOS-S-only verbs (`show inventory`, `show interfaces brief`, `show lldp neighbors detail`, `show switch info`, `show log buffer`, `show trunks`).
5. **Root cause, directly confirmed**: HOSTNAME-06 arrived at collection with `vendor="aruba"` already set (from the seed's LLDP classification), so the pre-fix gate (`vendor in auto/unknown`) never triggered an identity probe. Platform metadata was never populated, so DD-012's platform-aware profile selector could not engage even though the device's own `show version` output (item 1 of the wrong profile) proves it is ArubaOS-CX. The CX self-identification was captured but never fed back into command selection because the identity-probe step was skipped entirely for this neighbour.

## SW3 Determination

- Seed's parsed LLDP neighbours (`192.168.2.241/summary.json`, cross-checked against `show_lldp_neighbor-info_detail.txt`): 6 entries — one MAC-only entry, three UAP-AC-Pro APs, HOSTNAME-06, and "HOSTNAME-20" (GS748Tv5 switch). No SW3-class entity appears.
- HOSTNAME-06's own LLDP command (`show lldp neighbors detail`) **failed outright** (`Invalid input: neighbors`) — zero bytes of neighbour data were ever returned, so there is nothing to parse or classify downstream of HOSTNAME-06.
- **Verdict: SW3 is genuinely absent from all evidence in this bundle.** It is not present-but-unparsed, not present-but-unclassified, and not present-but-unqueued — the only mechanism that could have surfaced it (HOSTNAME-06's LLDP capture) never executed successfully.

## HOSTNAME-05 Determination

Does not exist in this bundle in any form. Cannot be assessed as "genuine neighbour" vs. "revisit/topology collapse" because there is no evidence of it at all — no device folder, no manifest entry, no console line, no topology node.

## MVP Assessment (this bundle only)

- One-hop-out achieved: seed → HOSTNAME-06 discovered, classified, authenticated, and collected (status `partial`, correctly health-penalised).
- Second-hop/downstream traversal not achieved in this bundle — fully and solely explained by the profile-misselection defect blocking HOSTNAME-06's own LLDP capture, not by any defect in discovery, classification, queueing, or traversal.

## Remediation Required?

**No new remediation.** The defect this bundle demonstrates is the same defect already fixed at current HEAD (commit `5fe7004`, containing the PHASE-084 `discovered_neighbor` identity-probe gate). This bundle was collected against `c290677`, which predates that fix. It is valid confirming evidence of the pre-fix baseline; it cannot be used to judge the fix, because it does not run the fixed code.

## Disposition

- PHASE-086 (`docs/Phases/PHASE-086-FieldValidationPost084-SecondHopTraversal.md`) remains the correct, already-defined next activity: a genuine field run against a build whose `build_provenance.json` records a commit at or after `5fe7004` (or `462bf43`/PHASE-085, which also contains the fix).
- No DDR change; no source or test change.
- Prior document `PHASE-086-EvidenceRejection-20260907.md` is superseded by this record; its "file not found" premise was incorrect, but its substantive conclusion (this bundle predates the fix) is independently confirmed here by direct bundle and git inspection.
