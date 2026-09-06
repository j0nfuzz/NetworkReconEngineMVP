PHASE:
PHASE-076-PortableBuildProvenancePropagation

STATUS:
Implemented

FILES MODIFIED:
- app/provenance.py: Added _load_runtime_provenance() and RUNTIME_PROVENANCE_PATH; get_head_commit_sha()/is_working_tree_dirty()/capture_provenance() now fall back to embedded build provenance when git is unavailable; capture_provenance() no longer shells out to git when capture is disabled.
- build_portable.py: Writes build_runtime_provenance.json next to build_manifest.json using the same build-time provenance payload.

TESTS ADDED:
- tests/test_provenance.py::test_capture_provenance_falls_back_to_runtime_file_when_git_unavailable

DDR UPDATES:
UNCHANGED DD:DD-008

RISKS INTRODUCED:
- Portable builds now rely on a static file for runtime provenance; rebuilding is required to update it after source changes.

RISKS RESOLVED:
- Field bundles from portable deployments no longer lose source identity when .git is absent.
- Disabled provenance capture no longer crashes tests/CI by shelling out to git.

OPEN ISSUES:
- None.
