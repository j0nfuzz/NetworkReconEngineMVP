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
