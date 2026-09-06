STATUS: DEFERRED (superseded in priority by PHASE-077; see PROJECT-JOURNAL 2026-09-06 reassessment). Provenance remains traceable via build_manifest.json/build lineage in the interim. Not implemented; may be picked up after PHASE-077.

PHASE:
PHASE-076-PortableBuildProvenancePropagation

FILES:
- app/provenance.py
- build_portable.py
- app/collector.py

ACCEPTANCE CRITERIA:
- Portable build embeds its build-time provenance (commit_sha, dirty, patch, patch_checksum) as a static artifact at build time.
- Runtime `capture_provenance()`/`write_provenance_artifact()` uses the embedded build-time provenance when running from a portable deployment (no `.git` present), instead of shelling out to git.
- Git-based capture behavior is unchanged for source checkouts with `.git` present.
- Field bundle `build_provenance.json` `head_commit_sha` matches the portable build's `build_manifest.json` `commit_sha` when run from the extracted portable bundle.
- Regression test proves provenance falls back to embedded build data when no `.git` directory is present.

CONSTRAINTS:
- No changes to timeout, SSH, recovery, traversal, or classification behavior.
- No changes to DD-008 semantics; only fixes propagation of already-approved provenance capture.
- Preserve existing `capture_provenance()` return shape.

KNOWN RISKS:
- Embedded provenance can go stale if the same portable build is reused indefinitely without rebuilding; acceptable since build_manifest.json already documents this tradeoff.

OUTSTANDING RISKS:
- Recursive-path artefact/console buffering (deferred writes/logging until traversal completes) remains unresolved; separate phase if still valued.

OPEN QUESTIONS:
- None.
