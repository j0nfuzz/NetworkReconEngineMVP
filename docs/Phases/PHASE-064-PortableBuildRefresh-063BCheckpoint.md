PHASE:
PHASE-064-PortableBuildRefresh-063BCheckpoint

OBJECTIVE:
Produce a new portable build from current HEAD (post-PHASE-063B) using the existing PHASE-060 packaging/provenance pipeline, verified as launch-ready and traceable, so field validation can proceed against current approved code.

FILES:
- build_portable.py (execution only; no logic changes expected)
- Generated build artefact / manifest

ACCEPTANCE CRITERIA:
- Build artefact generated from current HEAD (commit SHA matches `git log --oneline -1`).
- Provenance manifest present and correctly reflects commit SHA, build timestamp, and dirty/clean state (per DD-008-aligned provenance controls established in PHASE-060).
- Build launches and passes existing smoke/build tests (per PHASE-060 test suite, tests/test_build_portable.py).
- No source code modified as part of this phase.

CONSTRAINTS:
- Strictly packaging/build scope; any discovered defect must be deferred to a separate, explicitly-scoped engineering phase, not fixed inline.
- Must not alter DD-015 or any other approved decision.
- No changes to packaging logic, provenance mechanism, or manifest schema unless the rebuild reveals a defect.
- No changes to app/ source code.

KNOWN RISKS:
- If the rebuild surfaces a packaging defect (e.g., PHASE-060 tooling doesn't account for changes since), this phase's scope would need to expand — flag but do not resolve inline; escalate as a new phase instead.
- Low risk overall since PHASE-060 pipeline is already validated and unchanged.

OUTSTANDING RISKS:
- None beyond the above until rebuild is executed.

OPEN QUESTIONS:
- None.
