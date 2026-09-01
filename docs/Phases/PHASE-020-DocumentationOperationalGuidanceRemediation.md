PHASE:
DocumentationOperationalGuidanceRemediation

FILES:
README.md

ACCEPTANCE CRITERIA:
- README states that omitting --recursive performs flat, non-recursive per-device collection.
- README states that omitting --target-device runs recursive collection unscoped (sequential orchestrator, no topology-based limiting).
- README states that omitting --checkpoint-file runs collection without persisting or loading resume state.

CONSTRAINTS:
- README.md only.
- No new documentation topics.
- No code changes.

KNOWN RISKS:
- None (documentation-only change).

OUTSTANDING RISKS:
- --max-concurrent ceiling (10) not configurable; carried from PHASE-019.
- Cross-workstation bootstrap validation remains an open operational activity.

OPEN QUESTIONS:
- None.
