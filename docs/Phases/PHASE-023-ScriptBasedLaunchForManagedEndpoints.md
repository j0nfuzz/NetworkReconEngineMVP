PHASE:
ScriptBasedLaunchForManagedEndpoints

FILES:
docs/HOWTO-PORTABLE.md
README.md
interactive_bootstrap.ps1

ACCEPTANCE CRITERIA:
- HOWTO-PORTABLE.md documents a script-based launch path (bootstrap + source CLI) as the recommended method for ASR-restricted/managed endpoints.
- README.md records the <CUSTOMER> field-test finding (Defender ASR Rule 01443614 blocks unsigned .exe) as a known deployment constraint.
- No changes to app/cli.py, build_portable.py, or collection/packaging/checkpoint logic.
- Existing 64 tests continue to pass.

CONSTRAINTS:
- Documentation and bootstrap-invocation changes only; no new dependencies.
- Do not propose or implement code-signing.
- Do not modify existing .exe packaging pipeline.

KNOWN RISKS:
- Script-based launch still requires Python 3.12+ discoverable via PHASE-016 bootstrap; locked-down endpoints without PATH access remain unsupported.

OUTSTANDING RISKS:
- Unsigned executable may still be quarantined by endpoint protection (carried, now confirmed in production).
- Interactive prompts require a TTY; automation must use --config (carried).

OPEN QUESTIONS:
- Whether the target enterprise's Defender ASR policy can allow-list a specific script hash/path (owned by the customer, not this project).
