PHASE:
Topology Graph (PoC)

STATUS:
Implemented

FILES MODIFIED:
- app/topology.py (new)
- app/cli.py
- tests/test_cli.py

TESTS ADDED:
- tests/test_cli.py::test_build_topology_graph_links_connected_devices
- tests/test_cli.py::test_build_topology_graph_isolated_node
- tests/test_cli.py::test_build_topology_graph_empty_input

DDR UPDATES:
- UNCHANGED DD:2026-08-04

RISKS INTRODUCED:
- CDP/LLDP neighbour names may not match configured device names, producing edges to absent nodes.

RISKS RESOLVED:
- Neighbour data now represented as a deterministic graph for downstream traversal.

OPEN ISSUES:
- None.
