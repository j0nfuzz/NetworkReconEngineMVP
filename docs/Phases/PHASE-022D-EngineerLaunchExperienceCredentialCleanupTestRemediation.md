PHASE:
EngineerLaunchExperienceCredentialCleanupTestRemediation

FILES:
tests/test_cli.py

ACCEPTANCE CRITERIA:
- test_prompt_interactive_inventory_propagates_unlink_failure no longer leaves a temp inventory file on disk after it completes.
- The mocked unlink failure still asserts that the original OSError propagates from _prompt_interactive_inventory().
- test_prompt_interactive_inventory_unlinks_file_on_yaml_failure passes regardless of prior test run order.
- Full tests/test_cli.py suite passes with 64 tests, reproducibly across repeated runs.

CONSTRAINTS:
- No changes to app/cli.py.
- No changes to interactive prompt flow, console/packaging mode, or collection/traversal/checkpoint logic.
- Change budget: 1 file / 20 lines.

KNOWN RISKS:
- None; this is a test-only isolation fix.

OUTSTANDING RISKS:
- Unsigned executable may still be quarantined by endpoint protection (carried from PHASE-021).
- Interactive prompts require a TTY; automated runs must use --config (carried from PHASE-022A).

OPEN QUESTIONS:
- None.
