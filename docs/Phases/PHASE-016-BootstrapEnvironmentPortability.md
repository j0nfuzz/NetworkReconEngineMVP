PHASE:
BootstrapEnvironmentPortability

FILES:
interactive_bootstrap.ps1

ACCEPTANCE CRITERIA:
- Broken/stale .venv or .venv-legacy (missing/invalid interpreter) is detected and automatically recreated.
- Python is discovered via `py` launcher then PATH `python`, with no user-specific hard-coded paths.
- No usable Python 3.12+ produces an actionable message and exits before any SSH/collection attempt.
- Existing flow unaffected: -SkipInstall, -ParamikoProfile force, valid existing venvs reused without rebuild.

CONSTRAINTS:
- No new packaging/installer/container/dependency.
- No changes outside interactive_bootstrap.ps1.
- Preserve existing CLI parameters and script flow.

KNOWN RISKS:
- Fix is validated by code review + local run only; not yet confirmed on a genuinely separate clean workstation.

OUTSTANDING RISKS:
- Cross-workstation portability remains unverified in the field until tested on a machine without any prior Python/venv history.

OPEN QUESTIONS:
- Should discovery also accept Python 3.13+ interpreters for the modern profile, or pin strictly to 3.12?
