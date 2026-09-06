PHASE:
PHASE-077A-ScopedStreamingAndConsoleCaptureCompletion

STATUS:
Implemented

FILES MODIFIED:
- app/parallel_collector.py: Added on_device_collected callback parameter to run_parallel_scoped_collection_async() and run_parallel_scoped_collection(); callback is invoked per device after its bundle is added to the result set, passing device name, bundle, and checkpoint state.
- app/cli.py: Wired on_device_collected callback into the target-device scoped/parallel collection path; final "Generated bundle manifest" message is now routed through log_verbose (and therefore console.log) when verbose tee is active.

TESTS ADDED:
- tests/test_parallel_collector.py::test_on_device_collected_callback_fires_per_device
- tests/test_cli.py::test_scoped_cli_streams_device_bundle_before_traversal_completes
- tests/test_cli.py::test_bundle_manifest_message_captured_in_console_log

DDR UPDATES:
UNCHANGED DD:DD-008

RISKS INTRODUCED:
- None.

RISKS RESOLVED:
- Scoped/parallel collection now streams device bundles, manifest, and topology live instead of buffering until the wave completes.
- Final bundle-manifest message is persisted to console.log for both recursive and scoped paths.
- Existing sequential recursive behaviour is unchanged.

OPEN ISSUES:
- None.
