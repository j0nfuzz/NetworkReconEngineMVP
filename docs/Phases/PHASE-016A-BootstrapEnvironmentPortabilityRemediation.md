PHASE:
BootstrapEnvironmentPortabilityRemediation

FILES:
interactive_bootstrap.ps1
tests/test_bootstrap.ps1

ACCEPTANCE CRITERIA:
- Test-VenvHealthy returns false when pyvenv.cfg's home interpreter path does not exist, even if Scripts\python.exe is present.
- Test-VenvHealthy returns false when the venv python exits non-zero.
- A test isolates stale pyvenv.cfg detection without removing/renaming python.exe.
- Tests cover py-launcher precedence, PATH python fallback, and clean failure when no Python 3.12+ is found.

CONSTRAINTS:
- No changes outside interactive_bootstrap.ps1 and tests/test_bootstrap.ps1.
- Preserve existing Ensure-Venv behavior, CLI parameters, and discovery order.

KNOWN RISKS:
- Parsing pyvenv.cfg's `home` value assumes CPython's standard key name; format drift in future Python venv implementations is unhandled.

OUTSTANDING RISKS:
- Cross-workstation field verification remains pending (carried from PHASE-016).

OPEN QUESTIONS:
- None.
