PHASE:
FieldEvidenceSerializationVerification

STATUS:
Implemented

FILES MODIFIED:
- docs/Phases/PHASE-031-FieldEvidenceSerializationVerification.md
  - Created the architect phase definition artefact previously missing from the repository.
- app/normalization.py
  - build_device_summary() now copies failed_commands and failed_command_details from bundle.summary.
- app/troubleshooting.py
  - build_troubleshooting_bundle() now includes failed_commands and failed_command_details in the returned payload.
- tests/test_cli.py
  - Added test_failed_command_details_survive_into_bundle_artifacts covering summary.json, troubleshooting_bundle.json, and the device ZIP archive.
  - Added test_failed_command_partial_output_survives_in_bundle_artifacts covering partial stdout/stderr retention in the packaged command artefact.
- tests/test_normalization.py
  - Updated test_build_device_summary_deterministic_shape expected key set.
- tests/test_troubleshooting.py
  - Updated test_build_troubleshooting_bundle_deterministic_shape expected key set.

TESTS ADDED:
- tests/test_cli.py::test_failed_command_details_survive_into_bundle_artifacts
- tests/test_cli.py::test_failed_command_partial_output_survives_in_bundle_artifacts

DDR UPDATES:
UNCHANGED DD:DD-006

RISKS INTRODUCED:
- None.

RISKS RESOLVED:
- PHASE-030 evidence (elapsed_seconds, error_type, failed_command_details) now survives into on-disk and zipped review artefacts.
- Failed command partial output is regression-protected through the ZIP bundle path.

OPEN ISSUES:
- None.
