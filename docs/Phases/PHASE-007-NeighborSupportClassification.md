PHASE:
Neighbor Support Classification

FILES:
- app/discovery.py
- app/traversal.py (or new app/classification.py, implementer's choice)
- tests/test_cli.py

ACCEPTANCE CRITERIA:
- CDP neighbor parsing captures the existing "Platform:" line into each neighbor record (e.g. {"neighbor": "SW02", "platform": "cisco WS-C2960-24TC-L"})
- A new deterministic function maps neighbor platform/capability strings to one of: supported vendor (cisco/aruba/fortigate/juniper), "unsupported" (printers/UPS/phones/IoT/unknown), or "unknown" (no platform data)
- Function accepts the topology graph's neighbor list (or per-node discovered_neighbors) and returns a classification per neighbor name, without mutating existing graph/topology.json shape
- Unsupported/unknown devices are recorded, never dropped
- Tests cover: recognized cisco/aruba/fortigate/juniper platform strings, an unsupported device (e.g. printer/UPS string), and missing/empty platform data

CONSTRAINTS:
- No SSH connections, no credential handling (Phase 8), no recursive collection loop, no concurrency, no checkpointing
- No new dependencies
- Existing CDP/LLDP regex parsing and existing tests continue to pass unmodified
- Minimal, additive change to discovery.py capture only; do not restructure extract_neighbors() control flow

KNOWN RISKS:
- None beyond graph/discovery risks already carried

OUTSTANDING RISKS:
- CDP/LLDP neighbour names may not match configured device names, producing orphaned/failed traversal nodes (carried from PHASE-004/005/006)
- Platform string formats vary by vendor firmware version; classification heuristics may misclassify uncommon models

OPEN QUESTIONS:
- Whether classification results should be persisted alongside topology.json or computed on demand (deferred to Phase 7/8 wiring)
