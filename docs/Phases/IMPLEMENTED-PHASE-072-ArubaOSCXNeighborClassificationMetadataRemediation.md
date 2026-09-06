# IMPLEMENTED-PHASE-072-ArubaOSCXNeighborClassificationMetadataRemediation.md

## Phase

PHASE-072-ArubaOSCXNeighborClassificationMetadataRemediation

## Root Cause

PHASE-071 field evidence showed seed collection succeeded and topology.json retained neighbor addresses, but only the seed device was collected. Recursive traversal never advanced because `app/discovery.py::_parse_lldp_neighbors()` for ArubaOS-CX output extracted `neighbor` and `ip` but never `platform` or `capabilities`. `classify_neighbor_support()` requires those keys to classify a device as supported (`cisco`, `aruba`, etc.). Every neighbor therefore classified as `unknown`, so `run_recursive_collection()` did not enqueue any neighbor for SSH collection.

## Field-Evidence Mapping

| Observed Raw Field | Now Extracted | Used By | Example from FT060920261728 |
|---|---|---|---|
| Neighbor System-Description | `platform` | `classify_neighbor_support()` | `Aruba R8N85A  PL.10.11.1021` → `aruba` |
| Chassis Capabilities Available | `capabilities` | `classify_neighbor_support()` | `Bridge, Router` |
| Neighbor System-Name | `neighbor` | existing | `HOSTNAME-06` |
| Neighbor Management-Address | `ip` | existing | `192.168.2.242` |

## Files Changed

- `app/discovery.py`
- `tests/test_discovery.py`

## Changes

- Extended the ArubaOS-CX LLDP branch to read `Neighbor System-Description` and `Chassis Capabilities Available`.
- Populates `platform` from system description when present; falls back to existing chassis-id platform only when no description and no IP.
- Populates `capabilities` when available.
- Preserves PHASE-058 block/field parsing and PHASE-067 IP/name extraction.
- Added sanitised field-evidence-derived regression tests covering:
  - Populated system description + capabilities enable Aruba classification.
  - System description enables Cisco classification even without management IP.
  - Absent description preserves existing chassis-id platform fallback.
- Updated existing PHASE-058 test expectation to include the now-extracted fields.

## Validation

- `python -m py_compile app/discovery.py app/cli.py` passed.
- `python -m pytest tests/test_discovery.py tests/test_cli.py -q` passed: 125 passed.
- `python -m pytest -q` passed: 327 passed, 1 warning (pre-existing).

## Scope Confirmation

- No changes to `classify_neighbor_support()`.
- No changes to traversal logic.
- No changes to SSH logic.
- No changes to CLI behaviour.
- Additive parser field population only.
