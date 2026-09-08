# PHASE-086 Field Validation Findings — FT070920261340.zip

## Collection Metadata

- Bundle: `field_tests/FT070920261340.zip`, SHA-256 `4BD6ADFB7CDAB70549473B8FA1A563E5A56465928766E876B684AE1D9DD4972E`.
- All three device bundles record `build_provenance.json` head_commit_sha `462bf4366d0121b17209856059df9258bc428309`, dirty `false` — the PHASE-085 build. Confirmed genuine post-PHASE-084-fix evidence (unlike FT060920262050, which recorded `c290677`).
- Governance: field_tests/FIELDTEST.MD applied.

## Devices in Bundle

| Device (name) | Hostname | Status | Platform | Commands | Failed |
|---|---|---|---|---|---|
| `192.168.2.241` (seed) | 192.168.2.241 | collected | arubaos-cx | 11 | 0 |
| `HOSTNAME-06` | 192.168.2.242 | collected | arubaos-cx | 11 | 0 |
| `HOSTNAME-05` | 192.168.2.241 | collected | arubaos-cx | 11 | 0 |

## PHASE-084 Fix: Confirmed Working in the Field

- `console.log` shows `[verbose] HOSTNAME-06: probing identity... identity resolved: vendor=aruba` — the identity probe now runs for this classification-derived neighbour (absent in the pre-fix FT060920262050 bundle).
- `HOSTNAME-06/summary.json`: `platform: "arubaos-cx"`, `identity_confidence: 0.6`, `commands_run: 11` (the aruba-cx profile, not the 13-command AOS-Switch profile), `status: "collected"` (not `partial`), `failed_commands: []`.
- `HOSTNAME-06/show_lldp_neighbor-info_detail.txt` succeeded and returned a real, complete LLDP table ("Total Neighbor Entries : 4"), matching exactly 4 parsed `discovered_neighbors`.
- **Verdict: the PHASE-084 root cause is resolved. Second-hop devices with classification-derived vendor now receive correct platform-aware profile selection.**

## SW3 Determination (direct LLDP evidence)

`HOSTNAME-06`'s raw LLDP table contains exactly 4 entries, verified against the parsed `discovered_neighbors` count (4/4, no parser loss):

1. `HOSTNAME-04` (192.168.2.106) — AP, no CLI, correctly unsupported.
2. `00:11:22:33:44:a5` — no System-Name/Description (unmanaged endpoint), correctly unclassifiable.
3. `00:11:22:33:44:a6` — same as above.
4. `HOSTNAME-05` (192.168.2.241), System-Description `Aruba R8N85A PL.10.11.1021`, Port-Desc `LAG 2 to <LOCATION>` — **this is the seed device itself**, reached back over its LAG uplink (see Topology Collapse below).

**Verdict: SW3 does not exist in this bundle's evidence.** HOSTNAME-06 has no third switch-class LLDP neighbour beyond the link back to the seed. This is not a discovery, parsing, classification, or queueing failure — the physical LLDP table genuinely contains no further switch. The expected `SW1 → SW2 → SW3` topology does not match the physical network as evidenced; HOSTNAME-06's only switch-class link is back to the seed.

## New Defect: Same-Device Revisit / Topology Collapse (not previously evidenced)

Direct proof that `HOSTNAME-05` and the seed (`192.168.2.241`) are the same physical device, visited twice under two different name-keys:

- `HOSTNAME-05/summary.json` `hostname` = `192.168.2.241` (identical to the seed's own hostname).
- `HOSTNAME-05`'s `discovered_neighbors` list is identical to the seed's (same 10 entries, same IPs/platforms).
- `HOSTNAME-06`'s LLDP table reports its neighbour named `HOSTNAME-05` with Management-Address `192.168.2.241` and System-Description `Aruba R8N85A PL.10.11.1021` — matching the seed's own `show_system`/`show_version` identity exactly.
- `topology.json` contains three nodes (`192.168.2.241`, `HOSTNAME-06`, `HOSTNAME-05`) where two of them are provably the same physical box.

**Root cause (verified in code, not inferred)**: `app/orchestrator.py` deduplicates purely by `device.name` string —
```
visited.add(device.name)
...
if not neighbor_name or neighbor_name in visited or neighbor_name in queued:
```
There is no cross-check against a previously-visited device's resolved hostname/IP. Because the seed is keyed by its configured name (`192.168.2.241`, an IP-as-name) while its own LLDP System-Name (as reported by its neighbour) is `HOSTNAME-05`, the traversal treats them as two distinct devices and re-collects the identical physical switch a second time, consuming one extra SSH session/credential use and producing a bundle that reports 3 devices where only 2 physically exist.

This is not a re-opening of discovery/classification/queueing/traversal correctness in general — those mechanisms did exactly what they are designed to do (enqueue an unvisited name, collect it). The gap is the absence of an identity-equivalence check (hostname/IP) alongside the existing name-based check.

## MVP Assessment

MVP definition: point at a seed, collect evidence, traverse neighbours, collect downstream devices, generate usable troubleshooting artefacts.

**MVP is achieved by this bundle**: the seed was collected, HOSTNAME-06 was correctly discovered, classified, platform-identified, and fully collected with the correct 11-command aruba-cx profile and successful LLDP capture, and complete artefacts (summary, ai_prompt, troubleshooting_bundle, topology, manifest, console log) were generated for both real physical devices. This is the first fully-correct, evidence-proven two-hop collection in the project's field history.

The revisit-collapse defect does not block this achievement — it produces one redundant (but harmless and correctly-collected) duplicate entry, not a failure to collect real infrastructure.

## Remediation Justified?

**Yes, one phase**: deduplicate discovered neighbours against already-visited devices by resolved hostname/IP identity, not name alone, so the same physical device is not re-collected under an LLDP-reported alias. See `docs/Phases/PHASE-087-DeviceIdentityDeduplicationByHostname.md`.

Not reopened (field-proven, evidence-consistent in this bundle): discovery, classification, queueing, traversal, recursion, credential propagation, streaming, console capture, provenance, progress logging, and the PHASE-084 platform-propagation fix itself.
