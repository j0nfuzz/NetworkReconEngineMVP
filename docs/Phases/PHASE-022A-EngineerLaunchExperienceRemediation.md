PHASE:
EngineerLaunchExperienceRemediation

FILES:
app/cli.py
build_portable.py
tests/test_cli.py

ACCEPTANCE CRITERIA:
- build_portable.py no longer passes --noconsole; packaged executable has an attached console.
- _prompt_interactive_inventory() writes the runtime YAML to a securely created temp file (e.g. tempfile.NamedTemporaryFile / mkstemp), not into --output-dir.
- The temp inventory file is deleted after load_devices() reads it, in all exit paths (success, dry-run, exception).
- No plaintext password remains on disk after the CLI run completes.
- Existing --config workflows (source and packaged) unchanged.

CONSTRAINTS:
- No changes to collection, traversal, checkpoint, topology, or health-scoring logic.
- No changes to interactive_bootstrap.ps1.
- Change budget: stay under 5 files / 300 lines.

KNOWN RISKS:
- Console build re-exposes packaged executable to console-window flash/visibility; acceptable tradeoff for functional prompting.
- Temp-file cleanup must handle early-exit/exception paths to avoid credential residue.

OUTSTANDING RISKS:
- Unsigned executable may still be quarantined by endpoint protection (carried from PHASE-021).
- --max-concurrent ceiling (10) remains non-configurable (carried from PHASE-019).

OPEN QUESTIONS:
- None.
