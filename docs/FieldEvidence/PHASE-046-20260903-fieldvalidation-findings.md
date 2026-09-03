# PHASE-046 Field Evidence Findings

## Collection Metadata

- Phase: PHASE-046-MultiHopScopeFieldValidation
- Build commit: 38894c11561f3d407491445ceb2409c38c48e119 (PHASE-045 approved), dirty working tree (PHASE-046 documentation edits only)
- Config used: `config/devices.yml` (local, gitignored; identical placeholder inventory to PHASE-040: `sample-cisco-router` 192.168.2.1, `sample-juniper-router` 192.168.2.2, `sample-aruba-switch` 192.168.2.3)
- Reproduction commands:
  ```powershell
  .\.venv\Scripts\python.exe -m app.cli --config config\devices.yml --output-dir field_output_046 --recursive --target-device sample-cisco-router --scope-depth 2 --verbose
  .\.venv\Scripts\python.exe -m app.cli --config config\devices.yml --output-dir field_output_046b --recursive --target-device sample-cisco-router --scope-depth 3 --verbose
  ```
- Collection mode: live (dry_run: false)
- Collection status: unreachable (both runs)

## Limitation: No Real Multi-Hop Topology Available

The only device inventory reachable to this workstation is the same placeholder, non-existent IP range (`192.168.2.1-3`) already documented as unreachable in `docs/FieldEvidence/PHASE-040-20260903-183540-bundle-findings.md`. No CDP/LLDP-capable lab or production device is reachable from this environment.

Consequently:

- `sample-cisco-router` failed at the SSH transport stage (`[WinError 121] The semaphore timeout period has expired`), identical to PHASE-040.
- No commands were executed, so `discovered_neighbors` is empty and no genuine multi-hop topology could be produced by CDP/LLDP parsing.
- `topology.json` was generated but contains only the single unreachable seed node with `"neighbors": []`, because topology construction (PHASE-005/005A) derives edges exclusively from real discovered neighbours.

**This is a real, hardware-dependent constraint, not a code defect.** Per PHASE-046's explicit instruction, this limitation is documented rather than fabricating topology data.

## Evidence Successfully Gathered

Although no real multi-hop topology chain was reachable, the following field-observable behaviour of the `--target-device` / `--scope-depth` integration was verified end-to-end against the live CLI (not merely unit-test mocks):

### Case 1: `--scope-depth 2`, no pre-existing `topology.json`

| Field | Value |
|---|---|
| Topology source | None (first collection for this output directory; `output_root/topology.json` did not exist yet) |
| Target device | `sample-cisco-router` |
| Requested scope depth | 2 |
| Generated scope | `['sample-cisco-router']` |
| Expected scope | `[target]` only, per `_run_recursive_cli()`'s documented fallback: "if topology.json does not exist, scope = [target_device]" |
| Difference | None — matches documented fallback behaviour exactly |

### Case 2: `--scope-depth 3`, fresh output directory (same fallback path)

| Field | Value |
|---|---|
| Topology source | None (fresh `field_output_046b` directory) |
| Target device | `sample-cisco-router` |
| Requested scope depth | 3 |
| Generated scope | `['sample-cisco-router']` |
| Expected scope | `[target]` only (same fallback as Case 1) |
| Difference | None |

### Case 3: Post-collection `topology.json` shape (real, not synthetic)

After Case 1's collection, `topology.json` was written to disk containing the actual (empty) discovery result for the unreachable device:

```json
{
  "nodes": {
    "sample-cisco-router": {
      "vendor": "cisco",
      "role": "unknown",
      "neighbors": []
    }
  },
  "edges": []
}
```

This confirms the real `topology.json` schema produced by an unreachable/no-neighbour device matches the shape assumed by PHASE-045's synthetic test fixtures (`{"nodes": {name: {"neighbors": [...]}}, "edges": [...]}`), i.e. the production code path that `build_troubleshooting_scope()` consumes is schema-compatible with what PHASE-005A actually emits.

### Provenance Artifact Verification

`build_provenance.json` was generated and packaged inside `sample-cisco-router.zip` for Case 2 (the second run, after resetting `NRE_DISABLE_PROVENANCE`), confirming DD-008 provenance capture is unaffected by the `--scope-depth`/`--target-device` code path:

```json
{
  "head_commit_sha": "38894c11561f3d407491445ceb2409c38c48e119",
  "dirty": "true",
  "patch_checksum": "8403686781368341bc0404c07eb63a6f8ce48f91f456a98e5bca660fff50440d",
  "excluded_paths": "config/*.yml"
}
```

(Full patch content omitted here; it reflected only the PHASE-045/046 documentation deltas at capture time.)

## Scope-Depth Cases Not Field-Verifiable This Phase

The following required validation cases from PHASE-046 could **not** be exercised against real topology data, because no reachable device with real CDP/LLDP neighbours exists in this environment:

- Multi-hop traversal beyond the seed node (scope-depth 2/3 producing more than one device).
- Cycle handling on a real topology graph.
- Deterministic output ordering on a real multi-node topology.
- `target-device` scoping selecting a non-seed device from a real multi-device topology.

These behaviours remain verified only by PHASE-045's synthetic unit-test fixtures (`tests/test_scope.py`, 23 passing tests), which is evidence of correct code behaviour but not of correctness against real network topology data.

## Observations (Evidence Only)

1. Both live CLI runs reproduced the identical unreachable-device failure mode already documented in PHASE-040, using the same placeholder inventory.
2. The `--target-device`/`--scope-depth` fallback path (`topology.json` absent → `scope = [target_device]`) behaved exactly as coded in `app/cli.py`, regardless of the requested `--scope-depth` value (2 and 3 both produced the same single-device fallback scope).
3. A real `topology.json` was written to disk with the exact schema (`nodes`/`neighbors`/`edges`) that `build_troubleshooting_scope()` consumes, confirming schema compatibility between PHASE-005A's real output and PHASE-045's synthetic test fixtures.
4. `build_provenance.json` (DD-008) was generated and packaged normally during a `--target-device`/`--scope-depth` run, showing no interaction/regression between PHASE-045/046 and provenance capture.
5. No code path specific to multi-hop BFS traversal (`hops > 0` against a topology containing edges) was exercised by live evidence in this phase, because no real topology contained any edges.

## Findings (Evidence Only)

### 1. Real topology schema compatibility

**Supported conclusion:** The real `topology.json` produced by the existing collection pipeline uses the same `nodes`/`neighbors`/`edges` structure assumed by PHASE-045's `build_troubleshooting_scope()` and its synthetic test fixtures. No schema mismatch exists between the real pipeline and the multi-hop scoping code.

### 2. `--scope-depth` fallback behaviour when no topology exists

**Supported conclusion:** When `topology.json` does not yet exist for the output directory, `--scope-depth` (2 or 3) has no observable effect; the scope falls back to `[target_device]` exactly as documented in PHASE-045/PHASE-017. This matches designed behaviour, not a defect.

### 3. Multi-hop BFS traversal against real, edge-bearing topology data

**Inconclusive.** No reachable device in this environment produced a topology with any discovered neighbours/edges, so the BFS traversal logic itself (`hops > 0` walking real edges, cycle handling, deterministic ordering, non-seed target selection) could not be exercised against real field data in this phase. This is a hardware-reachability limitation, not a disproof of the PHASE-045 implementation.

### 4. Provenance artifact generation alongside multi-hop CLI flags

**Supported conclusion:** `build_provenance.json` (DD-008) is generated and packaged correctly during a `--target-device`/`--scope-depth` collection run; no interaction defect was observed.

### Summary Classification

| Hypothesis | Evidence Verdict |
|---|---|
| Real `topology.json` schema is compatible with `build_troubleshooting_scope()` | Supported |
| `--scope-depth` fallback (no topology) matches documented single-target behaviour | Supported |
| Multi-hop BFS traversal correctness against real, edge-bearing topology | Inconclusive (no reachable multi-neighbour device) |
| Provenance capture unaffected by multi-hop CLI integration | Supported |
| Multi-hop scoping is broken in the field | Not observed; no contradicting evidence found |

## Redactions

- Device hostnames/IPs shown above are the same non-functional placeholder values already present in the tracked `config/devices.yml.example` template; no real customer or production infrastructure was contacted.
- No credentials, live topology, or proprietary network data were exposed.
