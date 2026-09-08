# IMPLEMENTED-PHASE-087-DeviceIdentityDeduplicationByHostname

## Root Cause Summary

The sequential recursive collector (`app/orchestrator.py::run_recursive_collection`) and the parallel scoped collector (`app/parallel_collector.py::run_parallel_scoped_collection_async`) tracked only `device.name` in their `visited` and `queued` sets. When the same physical switch was reachable under two different identifiers — the seed's configured name/IP (`192.168.2.241`) and its LLDP-reported system-name (`HOSTNAME-05`) — the traversal treated them as two distinct devices and re-collected the identical hardware a second time. FT070920261340 field evidence proved this directly: both devices resolved to the same hostname/IP and produced identical neighbour lists.

This is a topology-quality / identity-equivalence defect, not a discovery, classification, queueing, traversal, credential, streaming, or provenance defect.

## Files Changed

- `app/orchestrator.py`
  - Added `_device_identity_set()` helper returning the case-normalised `{name, hostname}` equivalence set for a `Device`.
  - Added `known_identities` tracking visited/queued device identities (seed + resume `visited` + resume `pending`).
  - Before enqueueing a classification-derived neighbour, the neighbour's identity set is intersected with `known_identities`; a match means the neighbour is an alias of an already-known device and is skipped instead of queued.
  - Existing name-based `visited`/`queued` checks remain as the fallback when no resolved address is available.

- `app/parallel_collector.py`
  - Added the same `_device_identity_set()` helper.
  - Added the same `known_identities` tracking and intersection check before appending neighbours to `next_queue`.
  - `known_identities` is updated when devices are promoted from `next_queue` to the main `queue` so later waves see earlier-wave identities.

- `tests/test_orchestrator.py`
  - Added `test_alias_neighbor_matching_visited_ip_is_not_recollection` (PHASE-087 regression).
  - Added `test_distinct_neighbors_with_unique_addresses_still_traversed` (PHASE-087 regression).

- `tests/test_parallel_collector.py`
  - Added `test_parallel_alias_neighbor_matching_visited_ip_is_not_recollection` (PHASE-087 regression).
  - Added `test_parallel_distinct_neighbors_with_unique_addresses_still_traversed` (PHASE-087 regression).

## Validation Performed

- `python -m py_compile app/orchestrator.py app/parallel_collector.py tests/test_orchestrator.py tests/test_parallel_collector.py` — passed.
- `python -m pytest tests/test_orchestrator.py tests/test_parallel_collector.py -q` — 54 passed.
- `python -m pytest tests -q` — 350 passed, 1 pre-existing warning (`test_resolve_profile_key_reports_fallback`).

## Unified Diff Summary

Production changes are additive and localised:

- `app/orchestrator.py`: +28 lines (helper + identity tracking + intersection check before enqueue).
- `app/parallel_collector.py`: +27 lines (helper + identity tracking + intersection check before enqueue).
- No changes to classification, discovery/LLDP parsing, queueing of genuinely-new devices, the PHASE-084 identity-probe gate, credential handling, SSH/transport, checkpoint schema, topology generation, or CLI arguments.

## Regression Coverage Added

1. **Alias recollection prevented** — A seed named by IP (`192.168.2.241`) discovers a neighbour named `HOSTNAME-05` whose management IP resolves to the same `192.168.2.241`. The alias is not collected; only the seed and the distinct downstream device appear in `successful`/`bundles`.
2. **Alias suppression is transitive** — The downstream device also reports the same alias; it is still skipped because the seed's identity is already in `known_identities`.
3. **Distinct neighbours unaffected** — A seed discovering two neighbours with unique IPs (`10.0.0.2`, `10.0.0.3`) results in all three devices being collected.
4. Both sequential (`run_recursive_collection`) and parallel (`run_parallel_scoped_collection`) paths are covered.

## Before / After Behaviour

### Before

- Seed `192.168.2.241` collected.
- `HOSTNAME-06` collected; its LLDP table reports `HOSTNAME-05` at `192.168.2.241`.
- `HOSTNAME-05` queued and collected because its name differed from the seed's name.
- Topology contained three nodes, two of which represented the same physical switch, wasting one SSH session/credential use.

### After

- Seed `192.168.2.241` collected; its identity `{192.168.2.241}` enters `known_identities`.
- `HOSTNAME-06` collected.
- `HOSTNAME-05` (IP `192.168.2.241`) is recognised as an alias of the seed and is not queued for collection.
- The LLDP-observed edge from `HOSTNAME-06` to `HOSTNAME-05` remains in `HOSTNAME-06`'s `discovered_neighbors`, so topology generation continues to record the physical link.
- Legitimate distinct neighbours with unique addresses continue to traverse normally.

## Scope Confirmation

- **In scope**: identity-equivalence check before enqueueing neighbours; sequential and parallel paths; regression tests.
- **Out of scope (unchanged)**: classification, discovery/LLDP parsing, queueing of new devices, PHASE-084 identity-probe gate, credential propagation, SSH/transport, checkpoint schema, topology graph construction, CLI arguments, vendor profiles, health scoring, provenance, streaming.
- **Known limitation retained**: devices with multiple interfaces/management addresses that differ from the LLDP-reported address may still evade this check; this was accepted in the phase definition and is not addressed here.

## Proposed DDR Update

UNCHANGED DD:DD-016 (Proposed, awaiting GPT Reviewer approval).
