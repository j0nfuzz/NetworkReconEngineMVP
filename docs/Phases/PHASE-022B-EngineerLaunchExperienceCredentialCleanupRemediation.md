PHASE:
EngineerLaunchExperienceCredentialCleanupRemediation

FILES:
app/cli.py
tests/test_cli.py

ACCEPTANCE CRITERIA:
- yaml.safe_dump() failure after mkstemp() results in the temp file being deleted, not left on disk.
- Exception handler does not call os.close() on an fd already closed by os.fdopen()/the with-block.
- Original exception still propagates to the caller after cleanup.
- New test verifies no plaintext-credential temp file remains after a simulated write failure.

CONSTRAINTS:
- No changes to interactive prompt flow, console/packaging mode, or collection/traversal/checkpoint logic.
- Change budget: stay under 2 files / 60 lines.

KNOWN RISKS:
- os.unlink() itself could fail (e.g. permissions); acceptable to let that secondary exception propagate.

OUTSTANDING RISKS:
- Unsigned executable may still be quarantined by endpoint protection (carried from PHASE-021).
- Interactive prompts require a TTY; automated runs must use --config (carried from PHASE-022A).

OPEN QUESTIONS:
- None.
