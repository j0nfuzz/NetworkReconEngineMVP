PHASE:
FieldEvidenceBuildProvenance

FILES:
app/provenance.py
app/collector.py
tests/test_provenance.py

ACCEPTANCE CRITERIA:
- New provenance module captures HEAD commit SHA on every bundle-producing run.
- If the working tree is dirty, the module writes the full unified diff patch (not a hash-only fingerprint) to a provenance artifact in the bundle output directory.
- Provenance artifact includes a SHA-256 checksum of the stored patch for integrity verification.
- Files matching known credential-bearing paths (config/*.yml) are excluded from captured diff content.
- write_bundle() persists the provenance artifact next to summary.json for every device bundle.

CONSTRAINTS:
- Do not modify timeout, SSH, recovery, or vendor profile logic.
- Do not alter PHASE-034 evidence, interpretation, or conclusions.
- No git hooks, CI gating, or collection-blocking behaviour in this phase.

KNOWN RISKS:
- Diff patches may be large for big changesets; acceptable for evidence-phase-sized deltas.
- Naive diff capture could leak secrets if exclusion list is incomplete.

OUTSTANDING RISKS:
- PHASE-034's existing bundle remains unreconstructable retroactively; no backfill is in scope.

OPEN QUESTIONS:
- Should collection warn (not block) when the working tree is dirty above a size threshold?
