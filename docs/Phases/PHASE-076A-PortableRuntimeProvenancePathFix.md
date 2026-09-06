PHASE:
PHASE-076A-PortableRuntimeProvenancePathFix

FILES:
- app/provenance.py

ACCEPTANCE CRITERIA:
- `RUNTIME_PROVENANCE_PATH` resolves to the portable bundle root (where `build_portable.py` writes `build_runtime_provenance.json`), not the `python/` embedded-interpreter subdirectory.
- Regression test proves the runtime provenance fallback locates the file when the interpreter runs from `<bundle_root>/python/python.exe` and the file lives at `<bundle_root>/build_runtime_provenance.json`.
- Existing git-based provenance behavior (source checkouts with `.git`) is unchanged.

CONSTRAINTS:
- No changes to `build_portable.py` (it already writes to the correct location per Terra).
- No changes to timeout, SSH, recovery, traversal, or classification behavior.
- Preserve existing `capture_provenance()` return shape.

KNOWN RISKS:
- None beyond the existing accepted risk that embedded provenance can go stale if a build is reused without rebuilding.

OUTSTANDING RISKS:
- None once this lands; PHASE-076's original acceptance criteria are otherwise met.

OPEN QUESTIONS:
- None.
