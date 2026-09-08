# PHASE-088-MacAddressTableTopologyEnrichment

Status: Continuation backlog as of PHASE-090 (2026-09-08); not active in this frozen experiment repository.
Classification: Enhancement on the continuation Roadmap. Not an active implementation handover.

Continuation entry point: [CONTINUATION-HANDOVER.md](../../CONTINUATION-HANDOVER.md). Retained at this path for historical traceability; no implementation has been authorised or started here.
Activation gate: PHASE-089 evidence supports value, architect selects this activity, and DD-017/schema semantics receive reviewer consideration. This is not remediation for SW3 absence.

## Purpose

If later justified, expose MAC forwarding observations as evidence for topology investigation while preserving the existing neighbour graph. Reuse already-collected command output first. The present evidence does not justify converting MAC/OUI matches into physical links or starting a second active workstream.

## Phase boundary

In scope after activation: deterministic, platform-scoped parsing of existing full MAC-table output into separate observations retaining MAC, VLAN, port/LAG, entry type, source command and capture provenance. Absent, unsupported or count-only output must remain explicitly unavailable. Choose exact production files at activation from the established collector/parser layout; the previous speculative app/extractors.py scope is withdrawn.

Out of scope: OUI-only or single-port-to-physical-edge inference; new graph nodes or edges; enqueueing devices; SSH/profile changes; simultaneous multi-vendor implementation; discovery, classification, alias, credential or resume redesign. Correlation requiring a new graph contract needs a later evidence-backed definition.

## Deferred acceptance conditions

- A selected platform fixture yields complete MAC/VLAN/port/type observations with provenance and explicit malformed/unavailable evidence handling.
- Separate observations represent forwarding reachability only, never asserted physical adjacency or chassis identity.
- Synthetic and sanitised fixtures cover indirect downstream learning, multiple VLANs, LAGs, missing tables and ambiguous identities without creating topology edges or collection targets.
- LLDP/CDP output, identity deduplication, alias back-edges and traversal are unchanged when observations exist or are absent.
- Known limitations: ageing, snapshots taken at different times, multiple chassis/interface MACs, intermediate bridges and shared uplinks. Lack of a matching entry cannot establish device absence.

No production implementation is authorised by this deferred definition. PHASE-089 is also in the continuation backlog; if selected there, its outcome may defer or stop this proposal entirely.
