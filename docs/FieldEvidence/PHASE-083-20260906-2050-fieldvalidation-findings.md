# PHASE-083 Field Validation Findings (Post-081A Build)

## Collection Metadata

- Run: FT060920262050.zip, field activity 2026-09-06 (~20:50 local per bundle name)
- Build under test: PHASE-082 bundle (commit c290677, archive SHA-256 664CF1FC...8AC1C)
- build_provenance.json in both device bundles: head_commit_sha c290677ed6cb63170ad36440ef541de7f5ede836, dirty false — build fully attributable, PHASE-082 discipline honoured.
- Governance: field_tests/FIELDTEST.MD applied; identifiers used only at the precedent level already present in prior artefacts.

## Capabilities Proven by This Run

| Capability | Evidence |
|---|---|
| Credential propagation (PHASE-080) | HOSTNAME-06 authenticated with propagated credentials and executed 13 commands; branch no longer terminates at auth |
| Intra-device progress (PHASE-081/081A) | console.log shows probe/connect/(i/N) command lines for both devices; confidence-gated identity lines on the seed |
| Discovery/classification/queueing/traversal/recursion | Seed parsed 6 LLDP neighbours with distinct IPs; HOSTNAME-06 classified aruba, queued, collected |
| Streaming + console capture | Per-device artefacts and manifest streamed; console.log complete (37 lines) |
| Health-score penalty (PHASE-057) | HOSTNAME-06 partial status scored 85, not 100 |
| Evidence contract | failed_command_details present for all 6 failures (elapsed ~6s, transport active, error_type null) — device-side parser errors, not transport |
| Seed collection quality | aruba-cx profile 11/11 commands accepted, status collected |

## Defect — Neighbour platform metadata never resolved (single fault domain)

**Established facts:**
1. HOSTNAME-06 runs ArubaOS-CX (show_version banner: "ArubaOS-CX", Version PL.10.11.1021; show_system Product Name "R8N85A 6000 48G CL4 4SFP Swch").
2. Its summary records vendor aruba, platform unknown, identity_confidence 0.0 — no identity probe ran (console.log contains no identity lines for this device).
3. It executed the 13-command base aruba (AOS-Switch) profile. Six commands were rejected by the CX parser: show inventory, show interfaces brief, show lldp neighbors detail, show switch info, show log buffer, show trunks (five "Invalid input", one "% Ambiguous command."). All six are AOS-S verbs.
4. discovered_neighbors is empty; the LLDP artefact contains only the parser error. "SW3" appears nowhere in the bundle.

**Root cause:** app/orchestrator.py gates the identity probe on `device.vendor in ("auto","unknown")` (PHASE-061 wiring). Classification-derived neighbours arrive with vendor already set (aruba, from LLDP System-Description markers per PHASE-072), so the probe is skipped, identity metadata stays empty, and DD-012's platform-aware profile selection cannot engage. The parallel path does not have this gap (PHASE-055/055A probes every device in-session and passes platform).

**Consequence chain:** wrong profile -> LLDP command rejected -> zero neighbours parsed -> second-hop expansion impossible -> SW3 undiscovered. Discovery, parsing (PHASE-059/059A), classification, queueing, traversal and recursion remain field-proven and are NOT reopened; they were starved of input by the profile-selection defect.

**Not a defect:** the base aruba (AOS-Switch) profile itself — its rejections here occurred on CX hardware; no AOS-S hardware evidence exists either way (DD-013 position unchanged: AOS-S profile remains unvalidated).

## Observations (no phase raised)

- console.log emits per-device "Starting device"/"Finished collection" lines AFTER the command stream (callback placement carried from PHASE-073 streaming design); mildly misleading ordering — candidate observability polish, deferred.
- Seed model field misparsed as "2017-2023" (copyright-year regex, known detector cosmetic issue) — deferred.
- Failed CX commands each consumed ~6s device-side before returning parser errors.

## MVP Assessment

First field demonstration of the primary objective one hop out: point at one device -> complete package for that device plus a discovered, classified, authenticated, collected neighbour, with live progress, streamed artefacts, health penalty, and full build attribution. Not yet achieved end-to-end: second-hop infrastructure (SW3 downstream of HOSTNAME-06) blocked solely by the platform-propagation defect dispositioned below.

## Decision

One engineering phase is justified and sufficient: PHASE-084-NeighborIdentityPlatformPropagationRemediation. PHASE-083 closes by evidence.
