PHASE:
PortableDistribution

FILES:
build_portable.ps1
app/cli.py
docs/HOWTO-PORTABLE.md
README.md

ACCEPTANCE CRITERIA:
- A single Windows executable is produced containing the CLI and all runtime dependencies (no system Python required).
- Executable accepts the same arguments as `python -m app.cli` (--config, --output-dir, --recursive, --target-device, --checkpoint-file, --max-concurrent, --dry-run, --verbose, --probe).
- Documented workflow: download package, launch executable, provide device details, receive output bundle - no Git, Python, or venv steps.
- Existing interactive_bootstrap.ps1 / source-based workflow remains functional and unmodified in behaviour.

CONSTRAINTS:
- Windows-only for this phase.
- No new SSH/collection functionality; packaging only.
- Do not remove or alter interactive_bootstrap.ps1 behaviour.
- Change budget: stay under 10 files / 1000 lines.

KNOWN RISKS:
- PyInstaller bundling of asyncssh/paramiko may require explicit hidden-import declarations.
- Antivirus/SmartScreen may flag an unsigned executable.

OUTSTANDING RISKS:
- --max-concurrent ceiling (10) not configurable; carried from PHASE-019.
- Cross-workstation bootstrap validation remains an open operational activity (source-based path).

OPEN QUESTIONS:
- Should the packaged executable be distributed via GitHub Releases or a shared network location?
