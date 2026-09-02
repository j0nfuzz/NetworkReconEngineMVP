PHASE:
FieldEvidenceSerializationVerification

FILES:
app/normalization.py
app/troubleshooting.py
tests/test_cli.py
tests/test_normalization.py
tests/test_troubleshooting.py

ACCEPTANCE CRITERIA:
- build_device_summary() preserves failed_commands and failed_command_details from bundle.summary.
- build_troubleshooting_bundle() includes failed_commands and failed_command_details.
- summary.json contains failed_command_details with elapsed_seconds and error_type.
- troubleshooting_bundle.json contains failed_command_details with elapsed_seconds and error_type.
- The zipped device archive retains failed_command_details and failed command partial output.
- Existing 158 tests continue to pass; no behaviour change for successful commands.

CONSTRAINTS:
- Do not modify SSH settings.
- Do not modify timeout values.
- Do not modify command profiles.
- Do not add paging/prompt-detection logic.
- Do not investigate timeout causes.

KNOWN RISKS:
- Additional serialized fields increase bundle size negligibly.
- Partial output is still retained only in per-command raw artefacts, not duplicated inside failed_command_details.

OUTSTANDING RISKS:
- Scoped parallel collection (app/parallel_collector.py) remains outside this evidence contract.

OPEN QUESTIONS:
- None.
