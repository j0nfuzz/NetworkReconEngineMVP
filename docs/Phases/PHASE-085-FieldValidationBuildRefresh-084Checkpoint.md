PHASE:
PHASE-085-FieldValidationBuildRefresh-084Checkpoint

FILES:
- None modified (build/packaging activity only)
- Outputs: dist/NetworkReconEngine.zip, build_manifest.json (in-archive), docs/Phases/IMPLEMENTED-PHASE-085-FieldValidationBuildRefresh-084Checkpoint.md

PURPOSE:
Produce a clean, attributable portable build containing PHASE-084 (neighbour identity/platform propagation on the sequential recursive path) for the PHASE-086 field validation.

ACCEPTANCE CRITERIA:
- Working tree clean at HEAD before build; HEAD SHA recorded; full regression suite passes before and after the build.
- dist/NetworkReconEngine.zip rebuilt from clean HEAD using the default embedded-runtime mode; prior dist replaced.
- In-archive build_manifest.json: commit_sha equals build HEAD, dirty false, timestamp recorded.
- In-archive build_runtime_provenance.json at bundle root with head_commit_sha equal to manifest commit_sha.
- Extracted archive contains only config templates (no real *.yml).
- Packaged launchers (Start_NetworkRecon.ps1/.cmd --help) succeed from the extracted bundle.
- Packaged app/orchestrator.py contains the PHASE-084 gate (discovered_neighbor marker); packaged app/vendor_profiles.py contains the aruba-cx profile.
- Archive size and SHA-256 recorded; all evidence written to the IMPLEMENTED file.

CONSTRAINTS:
- No production or test code changes.
- No new features or dependencies.
- No reuse of prior dist.
- No credential-bearing files packaged or committed.

KNOWN RISKS:
- Static embedded provenance per build (accepted, documented).

OUTSTANDING RISKS:
- PHASE-084 behaviour remains field-unvalidated until PHASE-086 executes.
- AOS-Switch profile remains field-unvalidated.

OPEN QUESTIONS:
- None.

---

ARCHITECT AMENDMENT (environmental blocker, 2026-09-06):

- Blocker evidence: the canonical dist/NetworkReconEngine.zip (PHASE-082 build) is held by an exclusive lock. Restart Manager attribution identifies the holding process as ScreenConnect Client, PID 22664 (RmMainWindow). The RMM client is a live remote-access process and MUST NOT be terminated. Retry loops totalling >4 minutes did not release the handle.
- Amendment (PHASE-021 contract-amendment precedent): the PHASE-085 build is produced by build_portable.py from a pristine git worktree checkout of HEAD 462bf43 (tree CLEAN verified in situ), validated to the same acceptance criteria, and placed at dist/NetworkReconEngine-PHASE-085.zip. Provenance semantics are unchanged: manifest and runtime provenance both record commit 462bf43, dirty false.
- HAZARD CONTROL: dist/ temporarily contains TWO archives. dist/NetworkReconEngine.zip is the OLDER PHASE-082 build (commit c290677) and MUST NOT be deployed for PHASE-086. Field deployment must use dist/NetworkReconEngine-PHASE-085.zip verified against SHA-256 776B2527A1840C301EBB3074741EC1509FF2E50C138255365EE9F852E16BFC30.
- Follow-up action: when the ScreenConnect handle releases, replace the canonical name with the PHASE-085 artefact (or rebuild identically) and delete the amended-name duplicate so exactly one archive remains. This is a housekeeping action, not a new feature phase.
