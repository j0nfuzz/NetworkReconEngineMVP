PHASE:
FieldEvidenceBuildProvenance

STATUS:
Implemented

FILES MODIFIED:
- app/provenance.py (new)
  - Captures HEAD commit SHA, dirty flag, full unified diff patch, SHA-256 checksum, and excluded paths.
  - Excludes credential-bearing paths (config/*.yml) from patch content.
  - Supports enable/disable toggle and environment variable override (NRE_DISABLE_PROVENANCE).
- app/collector.py
  - Imports os and calls write_provenance_artifact() in write_bundle() before zipping.
  - Skips provenance capture when NRE_DISABLE_PROVENANCE is set (used in tests to avoid subprocess crashes).
- tests/test_provenance.py (new)
  - Tests for clean tree, dirty tree, checksum, exclusion handling, and artifact writing.
- tests/conftest.py (new)
  - Disables git-based provenance capture during pytest runs.
- docs/DESIGN-DECISION-REGISTER.md
  - Proposed DD-008.
- docs/PROJECT-JOURNAL.md
  - Appended PHASE-035 delta entry.

TESTS ADDED:
- tests/test_provenance.py (10 tests)

DDR UPDATES:
Decision ID: DD-008
Decision:
Every field-evidence collection run must automatically emit a provenance artifact containing the HEAD commit SHA and, if the working tree is dirty, the full uncommitted diff patch content plus a SHA-256 checksum of that patch.
Reason:
PHASE-034 review established that a diff fingerprint alone cannot reconstruct an uncommitted build; only durable, stored patch content is independently verifiable.
Status: Proposed
Date: 2026-09-03

RISKS INTRODUCED:
- Diff patches may be large for big changesets; acceptable for evidence-phase-sized deltas.
- Naive diff capture could leak secrets if the exclusion list is incomplete.

RISKS RESOLVED:
- Future field-evidence bundles can be reproduced from the exact source state that generated them.
- The PHASE-034 provenance blocker is resolved for future evidence collection phases.

OPEN ISSUES:
- PHASE-034's existing bundle remains unreconstructable retroactively; no backfill is in scope.
- No warning mechanism yet for very large dirty-tree diffs.
