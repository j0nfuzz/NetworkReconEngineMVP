PHASE:
PHASE-077-RecursiveLiveArtefactAndConsoleStreaming

STATUS:
Implemented

FILES MODIFIED:
- app/orchestrator.py: Added on_device_collected callback to run_recursive_collection(), invoked with device name, bundle, and checkpoint state immediately after each device completes.
- app/cli.py: Added _VerboseTee helper to print verbose lines to console and append to console.log; added _on_device_collected() to write device bundles, update bundle_manifest.json and topology.json, and emit start/finish logs live; recursive path now streams artefacts per device instead of buffering until traversal returns.

TESTS ADDED:
- tests/test_orchestrator.py::test_on_device_collected_callback_fires_per_device
- tests/test_cli.py::test_recursive_cli_writes_device_bundle_before_traversal_completes

DDR UPDATES:
UNCHANGED DD:DD-008

RISKS INTRODUCED:
- Slightly higher I/O frequency during recursive runs (one manifest/topology write per device); acceptable for expected device counts.
- console.log is append-only; long verbose runs produce larger files.

RISKS RESOLVED:
- Interrupted recursive runs now leave usable per-device bundles instead of losing all artefacts.
- Operators see live progress and have a persistent console log in the output directory.

OPEN ISSUES:
- None.
