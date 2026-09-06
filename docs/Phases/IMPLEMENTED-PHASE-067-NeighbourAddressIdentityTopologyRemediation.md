PHASE: PHASE-067-NeighbourAddressIdentityTopologyRemediation

STATUS: Implemented

IMPLEMENTATION SUMMARY:
Updated app/topology.py::build_topology_graph() to retain each discovered neighbor's "ip" field (when present) instead of discarding it.

Changes:
- Added "neighbor_addresses" dict to every node, mapping neighbor name -> IP when an IP is present.
- Appended an optional "ip" field to each edge when the underlying discovered_neighbors record contains one.
- Kept the existing "neighbors" list as strings and edge source/target naming unchanged for backward compatibility.

Added regression tests in tests/test_cli.py:
- test_build_topology_graph_preserves_neighbor_ip
- test_build_topology_graph_multiple_neighbors_keep_distinct_ips
- test_build_topology_graph_neighbor_without_ip_remains_compatible

VALIDATION:
- python -m py_compile app/topology.py tests/test_cli.py: passed
- pytest tests/test_cli.py -k "build_topology_graph": 7 passed
- Full pytest suite: 319 passed, 1 warning

FILES CHANGED:
- app/topology.py
- tests/test_cli.py

TESTS ADDED:
- tests/test_cli.py::test_build_topology_graph_preserves_neighbor_ip
- tests/test_cli.py::test_build_topology_graph_multiple_neighbors_keep_distinct_ips
- tests/test_cli.py::test_build_topology_graph_neighbor_without_ip_remains_compatible

DDR UPDATES:
UNCHANGED DD:2026-09-03

RISKS INTRODUCED:
- None expected; additive fields preserve existing consumers that ignore unknown keys.

RISKS RESOLVED:
- topology.json no longer silently loses neighbor management-address identity surfaced in bundle_manifest.json.

OPEN ISSUES:
- None.
