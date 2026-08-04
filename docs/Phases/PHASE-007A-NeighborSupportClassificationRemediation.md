PHASE:
Neighbor Support Classification Remediation (PoC)

FILES:
- app/discovery.py
- tests/test_cli.py

ACCEPTANCE CRITERIA:
- _parse_cdp_neighbors() captures the "Platform:" value when it is the final line of a CDP entry (no trailing newline, no ", Capabilities:" clause)
- Existing capture behaviour for platform lines followed by ", Capabilities:" or a newline remains unchanged
- classify_neighbor_support() correctly classifies a neighbor whose platform was only extractable via the fixed end-of-string case
- Existing PHASE-007 tests (platform capture, supported vendor recognition, unsupported devices, missing platform, non-mutation) continue to pass unmodified
- Regression test added covering a CDP entry where "Platform:" is the last line with no trailing delimiter

CONSTRAINTS:
- No new SSH commands, no credential handling, no recursive collection, no concurrency, no checkpointing
- No change to function signatures or neighbor record shape beyond the existing "platform" key
- No new dependencies
- Minimal fix only: adjust the platform regex terminator to also accept end-of-string; do not restructure CDP/LLDP parsing control flow

KNOWN RISKS:
- None beyond those already carried from PHASE-007

OUTSTANDING RISKS:
- CDP/LLDP neighbour names may not match configured device names, producing orphaned/failed traversal nodes (carried from PHASE-004/005/006)
- Platform string formats vary by vendor firmware version; classification heuristics may still misclassify uncommon models

OPEN QUESTIONS:
- None.
