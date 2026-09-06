# PHASE-079 Field Validation Findings (Post-076A/077A)

## Collection Metadata

- Run: FT060920261933.zip, generated 2026-09-06T18:28:50Z, live (dry_run: false)
- Build under test: PHASE-078 bundle (dist SHA-256 A62DBF8B...C5F94E)
- build_provenance.json in both device bundles: head_commit_sha 1bcd549dd5af244487d2de7785c1ca02ade3ede7, dirty false — matches build manifest and git HEAD at collection time. **Field evidence is fully attributable (DD-008 satisfied; PHASE-075 "unknown" failure mode eliminated).**
- Governance: field_tests/FIELDTEST.MD applied; identifiers used only as already present in prior review artefacts (REVIEW-PHASE-075 precedent).

## Capabilities Proven by This Run

| Capability | Evidence |
|---|---|
| Portable runtime provenance (PHASE-076/076A) | Both device bundles record the correct commit SHA |
| Discovery + classification (PHASE-059/059A/067/072) | 6 LLDP neighbour records from the seed; 5 with their own distinct IPs; HOSTNAME-06 classified vendor aruba |
| Queueing + traversal + recursion | HOSTNAME-06 discovered, queued, attempted; topology.json contains seed + HOSTNAME-06 nodes with neighbor_addresses mapping |
| Live artefact streaming + console capture (PHASE-073/077/077A) | console.log present with per-device Starting/Finished lines and final manifest message |
| Zip/artefact packaging | Per-device bundles and manifests complete |

## Defect 1 — No intra-device progress output

console.log contains exactly 5 lines: per-device Starting/Finished pairs plus the final manifest message. Between "Starting device" and "Finished collection" —covering SSH probe, identity probe, connect, and up to 11 command executions — there is no output of any kind. Operators receive per-device granularity but no feedback during the longest silent periods (auth waits, per-command timeouts). Classification: **implementation gap** (PHASE-073 scoped to per-device logging; intra-device granularity was never implemented). Justifies engineering phase PHASE-081.

## Defect 2 — Neighbour credentials not propagated (interactive journey)

HOSTNAME-06 result: vendor aruba, status unreachable, error "Authentication failed.", commands_run 0, no raw artefacts. The operator confirms seed credentials were expected to work on this device. Root cause (code-level): the interactive runtime YAML written by `app/cli.py:_prompt_interactive_inventory()` contains a `devices:` block only; no `default:` credentials block exists, so `load_default_credentials()` returns empty and both orchestrators build neighbour `Device` objects with empty username/password. Classification: **implementation defect** — credentials are *not propagated* on the default field journey. Justifies engineering phase PHASE-080.
Field hygiene note: empty-credential attempts generate failed-authentication entries in target device logs (observed in seed logging output); the same seed logs also show older unrelated auth-failure retries from January 2026.

## Non-Defects / No Reopening

- The sixth neighbour record (MAC-address identifier, no ip/capabilities) remains handled per PHASE-069 disposition: recorded, not queued. No new evidence changes that disposition.
- Ubiquiti/Netgear neighbours classify unknown and remain intentionally unqueued (REVIEW-PHASE-075 outstanding risk — unchanged).
- Discovery, classification, queueing, traversal, recursion, streaming, provenance: all supported by evidence; none reopened.

## Decision

Field validation executed against the PHASE-078 build; capabilities above proven; two implementation defects dispositioned to PHASE-080 (credentials) and PHASE-081 (intra-device progress). PHASE-079 closes by evidence.
