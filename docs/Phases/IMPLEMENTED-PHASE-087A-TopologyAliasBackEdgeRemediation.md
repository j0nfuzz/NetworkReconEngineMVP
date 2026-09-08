# IMPLEMENTED-PHASE-087A-TopologyAliasBackEdgeRemediation

## Root Cause Summary

PHASE-087 successfully prevented the collection path from recollecting a device already represented under a different name (e.g. seed `192.168.2.241` versus LLDP-reported alias `HOSTNAME-05`). However, the topology graph was still built from the raw LLDP neighbour record, so the alias name was emitted as a dangling edge target even though no corresponding node existed. This produced a graph identity split and an incorrect back-edge representation.

Root cause: `app/topology.py::build_topology_graph()` unconditionally used `neighbor_record.get("neighbor")` as the edge target without resolving it against already-collected device identities.

## Files Changed

- `app/topology.py`
  - Added `_build_identity_to_name_map()` to build a case-insensitive canonical-name map from collected summaries (`device` name + `hostname`).
  - Extended `build_topology_graph()` with an optional `identity_to_name` parameter (auto-built from summaries when omitted).
  - Neighbor records whose IP or name matches a known identity now resolve to the canonical node name.
  - Preserved the LLDP-reported alias name and management address as edge evidence (`alias` field, `ip` field).
  - Distinct neighbours with no identity overlap continue to be emitted unchanged.

- `tests/test_cli.py`
  - Added `test_build_topology_graph_resolves_alias_to_canonical_node_by_ip`
  - Added `test_build_topology_graph_resolves_alias_to_canonical_node_by_hostname`
  - Added `test_build_topology_graph_distinct_neighbor_unchanged`
  - Added `test_build_topology_graph_no_duplicate_node_from_alias`

## Validation Performed

- `python -m py_compile app/topology.py tests/test_cli.py` — passed.
- `python -m pytest tests/test_cli.py -k "build_topology_graph" -q` — 11 passed.
- `python -m pytest -q` — 354 passed, 1 existing warning (`test_resolve_profile_key_reports_fallback`).

## Unified Diff Summary

### `app/topology.py`

- Introduced `_build_identity_to_name_map(summaries)`.
- `build_topology_graph()` now resolves neighbor target via identity map:
  - `identity_key = neighbor_ip or neighbor_name`
  - `canonical = aliases.get(str(identity_key).lower())`
  - `target = canonical if canonical else neighbor_name`
- Edge now includes `"alias": neighbor_name` only when resolved to a different target.
- `nodes[source]["neighbors"]` and `neighbor_addresses` now use the resolved canonical target.

### `tests/test_cli.py`

- Four new regression tests prove:
  1. Alias resolved by matching IP becomes a back-edge to the canonical node.
  2. Alias resolved by matching hostname becomes a back-edge to the canonical node.
  3. Unique neighbours without identity overlap are unchanged.
  4. No duplicate logical node is created for an alias.

## Regression Coverage Added

1. Alias neighbour name resolves to an existing node identity (by IP and by hostname).
2. Back-edge is emitted to the canonical node.
3. No duplicate logical node is created.
4. Legitimate unique neighbours remain unchanged.

## Before/After Topology Behaviour

### Before (raw LLDP name as target)

```text
Nodes: 192.168.2.241, HOSTNAME-06, HOSTNAME-05
Edges: HOSTNAME-06 -> HOSTNAME-05 (dangling target)
```

`HOSTNAME-05` has no node entry, creating a dangling reference.

### After (alias resolved to canonical node)

```text
Nodes: 192.168.2.241, HOSTNAME-06
Edges: HOSTNAME-06 -> 192.168.2.241
        alias: HOSTNAME-05
        ip: 192.168.2.241
```

The edge now targets the existing collected node, while the original LLDP alias and management address are retained as evidence.

## Scope Confirmation

- PHASE-087 collection-path deduplication logic in `app/orchestrator.py` and `app/parallel_collector.py` is unchanged.
- No changes to discovery, LLDP parsing, classification, queueing, credential propagation, streaming, or provenance.
- No traversal, graph-engine, or topology redesign.
- No SSH or credential changes.
- Minimal remediation limited to `app/topology.py` and regression tests.

## Proposed DDR Updates

UNCHANGED DD:DD-016

DD-016 remains Rejected until a reviewer approves the combined PHASE-087/087A behaviour. The topology alias/back-edge gap is now remediated; the proposed next step is reviewer re-assessment and, if accepted, re-approval of DD-016.
