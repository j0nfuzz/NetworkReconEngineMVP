PHASE:
BootstrapEnvironmentPortability

STATUS:
Implemented

FILES MODIFIED:
- interactive_bootstrap.ps1
- tests/test_bootstrap.ps1 (new)

TESTS ADDED:
- Find-PythonInterpreter discovers an existing python executable
- Test-VenvHealthy returns false for missing venv directory
- Test-VenvHealthy returns true for freshly created healthy venv
- Test-VenvHealthy returns false when pyvenv.cfg exists but interpreter is missing
- Test-VenvHealthy returns false when pyvenv.cfg references a stale interpreter path
- Ensure-Venv creates a new venv when none exists
- Ensure-Venv reuses a healthy venv without recreating
- Ensure-Venv recreates a stale venv automatically

DDR UPDATES:
DD-004 Proposed

RISKS INTRODUCED:
- None beyond the existing PoC risk that venv recreation takes time on slow machines.

RISKS RESOLVED:
- Copied/synced .venv or .venv-legacy directories with stale interpreter references are detected and rebuilt automatically.
- Bootstrap no longer relies on a hard-coded or PATH-only python invocation; it uses `py` launcher first, then PATH `python`.
- Missing Python produces a clean, actionable error before any collection attempt.

OPEN ISSUES:
- Cross-workstation field verification on a clean machine without prior Python/venv history is still pending.
- Python 3.13+ discovery is allowed by the current code but not explicitly tested or required.
