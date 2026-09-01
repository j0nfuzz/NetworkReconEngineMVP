PHASE:
DocumentationOperationalGuidanceRemediation

STATUS:
Implemented

FILES MODIFIED:
- README.md

DOCUMENTATION ADDED:
- Default statement for --recursive (omitting performs flat, non-recursive per-device collection)
- Default statement for --target-device (omitting runs recursive collection unscoped using sequential orchestrator without topology-based limiting)
- Default statement for --checkpoint-file (omitting runs collection without loading or saving checkpoint state)

TESTS ADDED:
- None (documentation-only phase)

DDR UPDATES:
UNCHANGED DD:DD-005

RISKS INTRODUCED:
- None (no code changes)

RISKS RESOLVED:
- README no longer leaves flag default behaviour implicit for --recursive, --target-device, and --checkpoint-file.

OPEN ISSUES:
- None.
