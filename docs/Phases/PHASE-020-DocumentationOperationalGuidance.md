PHASE:
DocumentationOperationalGuidance

FILES:
README.md

ACCEPTANCE CRITERIA:
- README documents --recursive, --target-device, --checkpoint-file, --max-concurrent flags with purpose and defaults.
- README explains checkpoint/resume behaviour and scoped vs sequential collection.
- README documents summary.json, troubleshooting_bundle.json, and health score output fields.
- Documentation reflects only implemented behaviour (no aspirational content).

CONSTRAINTS:
- No code changes.
- No new files beyond README.md edits.
- Written for network engineers, not developers.

KNOWN RISKS:
- None (documentation-only change).

OUTSTANDING RISKS:
- --max-concurrent ceiling (10) not configurable; carried from PHASE-019.
- Cross-workstation bootstrap validation remains an open operational activity.

OPEN QUESTIONS:
- Should Phase 18 (Portable Distribution) be scheduled next once documentation lands?
