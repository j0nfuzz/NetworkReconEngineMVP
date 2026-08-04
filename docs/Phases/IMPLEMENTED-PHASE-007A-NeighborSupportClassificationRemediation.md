PHASE: PHASE-007A-NeighborSupportClassificationRemediation

STATUS: Implemented

FILES MODIFIED:
- app/discovery.py
  - _parse_cdp_neighbors() platform regex now accepts end-of-string ($) as a terminator, so final `Platform:` lines without a trailing newline or capabilities clause are captured.
- tests/test_cli.py
  - Added regression test for a CDP entry whose `Platform:` line is the last line of the output string, verifying both platform capture and downstream `cisco` classification.

TESTS ADDED:
- tests/test_cli.py::test_extract_neighbors_cisco_cdp_captures_platform_at_end_of_string

DDR UPDATES:
- UNCHANGED DD:2026-08-04

RISKS INTRODUCED:
- None.

RISKS RESOLVED:
- CDP platform value lost when `Platform:` was the final line of a CDP entry, causing incorrect "unknown" classification.

OPEN ISSUES:
- CDP/LLDP neighbor names may not match configured device names, producing orphaned/failed traversal nodes (carried from PHASE-004/005/006).
- Platform string formats vary by vendor firmware version; classification heuristics may still misclassify uncommon models (carried from PHASE-007).
