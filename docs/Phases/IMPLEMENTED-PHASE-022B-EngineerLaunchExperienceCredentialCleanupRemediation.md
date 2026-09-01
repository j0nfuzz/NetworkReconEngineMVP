PHASE:
EngineerLaunchExperienceCredentialCleanupRemediation

STATUS:
Implemented

FILES MODIFIED:
- app/cli.py
  - Fixed _prompt_interactive_inventory() exception path so yaml.safe_dump() failures delete the temp file and re-raise the original exception.
  - Replaced os.close(fd) + bare raise with runtime_path.unlink(missing_ok=True) wrapped in a defensive try/except OSError, then raise.
  - Converted runtime_path to Path immediately after mkstemp() so cleanup targets the correct file object.
  - Removed the double-close risk: the fd is now owned exclusively by the os.fdopen() context manager.
- tests/test_cli.py
  - Added tempfile and yaml imports.
  - Added test_prompt_interactive_inventory_unlinks_file_on_yaml_failure.

FILES ADDED:
- docs/Phases/IMPLEMENTED-PHASE-022B-EngineerLaunchExperienceCredentialCleanupRemediation.md

VALIDATION EVIDENCE:
- tests/test_cli.py: 63 passed (previously 62; 1 new cleanup test added).
- get_errors reported no errors in app/cli.py or tests/test_cli.py.

TESTS ADDED:
- test_prompt_interactive_inventory_unlinks_file_on_yaml_failure

DDR UPDATES:
UNCHANGED DD:DD-005

RISKS INTRODUCED:
- None.

RISKS RESOLVED:
- Plaintext credential temp file is no longer left on disk if YAML serialization fails.
- Original exception propagates without replacement or suppression.
- os.close() is no longer called on an fd already closed by os.fdopen()/the context manager.

OPEN ISSUES:
- None.
