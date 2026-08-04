PHASE: PHASE-007-NeighborSupportClassification

STATUS: Implemented

FILES MODIFIED:
- app/discovery.py
  - _parse_cdp_neighbors() now captures the "Platform:" field into each neighbor record as "platform".
- app/classification.py
  - Added classify_neighbor_support(neighbor_record): maps platform/capabilities strings to supported vendor (cisco/aruba/fortigate/juniper), "unsupported", or "unknown".
  - Added classify_neighbors(neighbors): returns deterministic classification per neighbor name without mutating input records.
- tests/test_cli.py
  - Imported classify_neighbor_support and classify_neighbors.
  - Added tests for CDP platform capture, supported vendor recognition, unsupported device detection, empty/missing platform data, per-neighbor classification mapping, and non-mutation of input.

TESTS ADDED:
- tests/test_cli.py::test_extract_neighbors_cisco_cdp_captures_platform
- tests/test_cli.py::test_classify_neighbor_support_recognizes_supported_vendors
- tests/test_cli.py::test_classify_neighbor_support_marks_unsupported_devices
- tests/test_cli.py::test_classify_neighbor_support_unknown_when_no_platform
- tests/test_cli.py::test_classify_neighbors_returns_classification_per_name
- tests/test_cli.py::test_classify_neighbors_does_not_mutate_input

DDR UPDATES:
- UNCHANGED DD:2026-08-04

RISKS INTRODUCED:
- CDP "Platform:" regex may not match every vendor format; unmatched platforms fall back to "unknown", which is safe.
- Supported-vendor keyword matching may misclassify uncommon or rebranded hardware; Phase 7 can refine this with runtime detection.

RISKS RESOLVED:
- None.

OPEN ISSUES:
- Classification results are computed on demand; whether they should be persisted in topology.json or bundle summaries remains deferred to Phase 7/8 wiring.
