PHASE:
PHASE-076A-PortableRuntimeProvenancePathFix

STATUS:
Implemented

FILES MODIFIED:
- app/provenance.py: Changed RUNTIME_PROVENANCE_PATH from Path(sys.executable).parent (python/) to Path(sys.executable).parent.parent (bundle root) so it matches the location where build_portable.py writes build_runtime_provenance.json.

TESTS ADDED:
- tests/test_provenance.py::test_runtime_provenance_resolves_to_bundle_root_in_portable_layout

DDR UPDATES:
UNCHANGED DD:DD-008

RISKS INTRODUCED:
- None.

RISKS RESOLVED:
- Portable extracted runs no longer fail to locate build_runtime_provenance.json because it was looked for under python/.
- Field bundles from portable deployments now record the actual build commit SHA instead of "unknown" when .git is absent.

OPEN ISSUES:
- None.
