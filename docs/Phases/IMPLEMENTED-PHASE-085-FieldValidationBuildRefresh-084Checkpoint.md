PHASE:
PHASE-085-FieldValidationBuildRefresh-084Checkpoint

STATUS:
Implemented (build/packaging activity only - no source or test code changes; executed under the recorded Architect environmental-blocker amendment)

BUILD PROVENANCE:
- Build source: pristine git worktree at HEAD 462bf4366d0121b17209856059df9258bc428309; in-situ `git status --porcelain` CLEAN and HEAD verified from inside the worktree before building.
- Reason for worktree build: canonical dist/NetworkReconEngine.zip (PHASE-082 build) is exclusively locked by ScreenConnect Client PID 22664 (Restart Manager evidence recorded in the PHASE-085 amendment); the live RMM client must not be terminated; >4 minutes of retries did not release the handle. Worktree build produced the identical contract artefact via the unmodified default embedded-runtime mode.
- Worktree removed after the build (registry clean; residual metadata directory removed manually after a transient permission error).
- Build timestamp: 2026-09-06T20:45:14Z (from build_manifest.json).
- Contains: PHASE-084 neighbour identity/platform propagation plus all approved work through PHASE-082.

MANIFEST EVIDENCE (in-archive build_manifest.json):
- commit_sha: 462bf4366d0121b17209856059df9258bc428309 (matches build HEAD)
- dirty: "false"; patch_checksum: ""; excluded_paths: config/*.yml

RUNTIME PROVENANCE EVIDENCE (in-archive build_runtime_provenance.json):
- Present at bundle root; head_commit_sha 462bf43... matches build_manifest.json commit_sha; dirty "false".

ARTEFACT EVIDENCE:
- Placed: dist/NetworkReconEngine-PHASE-085.zip (amended name per amendment): 29,408,886 bytes
- SHA-256: 776B2527A1840C301EBB3074741EC1509FF2E50C138255365EE9F852E16BFC30
- HAZARD: dist/NetworkReconEngine.zip (canonical name) currently still holds the OLDER PHASE-082 build (commit c290677) because the file is locked. Field deployment for PHASE-086 MUST use NetworkReconEngine-PHASE-085.zip verified against the SHA above. The canonical file must be replaced with (or rebuilt identically to) the PHASE-085 artefact as soon as the lock releases, and the duplicate removed; recorded as the immediate follow-up housekeeping action.
- Size differential vs the PHASE-082 archive (29,408,886 vs 29,503,838 bytes) recorded for transparency; both contain app/__pycache__ staging; content identity for this phase is asserted by manifest/provenance SHA agreement, config hygiene, launcher validation, and code spot-checks rather than byte-equality with the prior build.

CONFIG-HYGIENE EVIDENCE (extracted archive config/):
- devices.yml.example, interactive_devices.yml.example only; no real *.yml.

LAUNCHER VALIDATION EVIDENCE:
- Start_NetworkRecon.ps1 --help: succeeded from the extracted bundle.
- Start_NetworkRecon.cmd --help: succeeded from the extracted bundle.

CONTENT SPOT-CHECKS (packaged source):
- app/orchestrator.py contains the PHASE-084 discovered_neighbor probe gate: TRUE.
- app/vendor_profiles.py contains the aruba-cx profile: TRUE.

FILES MODIFIED:
- None (build/packaging activity only)
- Outputs: dist/NetworkReconEngine-PHASE-085.zip; PHASE-085 amendment section (Architect); this IMPLEMENTED record.

TESTS ADDED:
- None (phase constraints)
- Validation: full pytest suite 346 passed, 1 pre-existing warning - in the main repository before the build and after the build (code identical: HEAD unchanged at 462bf43 throughout).

DDR UPDATES:
UNCHANGED DD:DD-008

RISKS INTRODUCED:
- Two archives temporarily coexist in dist/ under different names (deployment-confusion hazard; controlled by explicit hazard documentation and the follow-up replacement action).

RISKS RESOLVED:
- A field-attributable build containing PHASE-084 now exists despite the environmental lock.

OPEN ISSUES:
- Replace the locked canonical dist/NetworkReconEngine.zip with the PHASE-085 artefact and remove the duplicate once the ScreenConnect handle releases.
- PHASE-086 field validation pending field access with the PHASE-085 artefact.
