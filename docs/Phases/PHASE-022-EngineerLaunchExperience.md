PHASE:
EngineerLaunchExperience

FILES:
app/cli.py
run_portable.py
README.md
docs/HOWTO-PORTABLE.md

ACCEPTANCE CRITERIA:
- Running the packaged executable with no --config prompts for hostname, username, port, password, and vendor (default "auto").
- Prompted input is written to a temporary runtime YAML consumed by the existing load_devices/collection path; no changes to collection internals.
- Existing --config-based invocation (source and packaged) continues to work unchanged for scripted/automated use.
- Documentation describes the extract -> launch -> enter details -> collect -> receive bundle flow without referencing config file authoring as a required first step.

CONSTRAINTS:
- No changes to interactive_bootstrap.ps1 behaviour.
- No new SSH/collection functionality; input-gathering only.
- Password must not be echoed or logged in plaintext.
- Change budget: stay under 10 files / 1000 lines.

KNOWN RISKS:
- Packaged executable has no PowerShell secure-prompt equivalent; must use a console-safe input method (e.g. getpass) that works inside a PyInstaller console build.

OUTSTANDING RISKS:
- --max-concurrent ceiling (10) remains non-configurable; carried from PHASE-019.
- Unsigned executable may still be quarantined by endpoint protection on other workstations.

OPEN QUESTIONS:
- Should interactive mode support entering multiple devices in one session, or remain single-device per PHASE-021's onedir scope?
