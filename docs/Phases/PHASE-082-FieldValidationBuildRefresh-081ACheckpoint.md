PHASE:
PHASE-082-FieldValidationBuildRefresh-081ACheckpoint

FILES:
- None modified (build/packaging activity only)
- Outputs: dist/NetworkReconEngine.zip, build_manifest.json (in-archive), docs/Phases/IMPLEMENTED-PHASE-082-FieldValidationBuildRefresh-081ACheckpoint.md

PURPOSE:
Produce a clean, attributable portable build containing PHASE-080 (interactive default credential propagation), PHASE-081/081A (intra-device progress logging with confidence-gated identity lines), and all prior approved work, for the next field validation run targeting:
- HOSTNAME-06 branch re-attempt with propagated credentials
- Intra-device verbose progress visibility in console.log during active collection

ACCEPTANCE CRITERIA:
- Working tree clean at HEAD before build; HEAD SHA recorded; full regression suite passes before and after the build.
- dist/NetworkReconEngine.zip rebuilt from clean HEAD using the default embedded-runtime mode; prior dist replaced.
- In-archive build_manifest.json: commit_sha equals build HEAD, dirty false, timestamp recorded.
- In-archive build_runtime_provenance.json at bundle root with head_commit_sha equal to manifest commit_sha.
- Extracted archive contains only config templates (no real *.yml).
- Packaged launchers (Start_NetworkRecon.ps1/.cmd --help) succeed from the extracted bundle; the packaged CLI surface includes --no-recurse/--target-device/--scope-depth/--max-concurrent/--verbose.
- Archive size and SHA-256 recorded; all evidence written to the IMPLEMENTED file.

CONSTRAINTS:
- No production or test code changes.
- No new features or dependencies.
- No reuse of prior dist.
- No credential-bearing files packaged or committed.

KNOWN RISKS:
- Static embedded provenance goes stale if the bundle is reused after source changes (accepted, documented).

OUTSTANDING RISKS:
- Field validation of PHASE-080/081/081A behaviour remains open until executed against this build.
- Parallel/scoped intra-device progress remains deferred.
- HOSTNAME-06 access depends on operator credential correctness in the field.

OPEN QUESTIONS:
- None.
