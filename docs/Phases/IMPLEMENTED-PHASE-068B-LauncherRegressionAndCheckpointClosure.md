PHASE:
PHASE-068B-LauncherRegressionAndCheckpointClosure

STATUS:
Implemented

FILES MODIFIED:
tests/test_build_portable.py
- Replaced duplicated launcher-text fixture tests with a production-coupled test that invokes build_portable._build_embedded() directly.
- Added helpers to stage a minimal repo, create a fake embedded python layout, and mock network/subprocess dependencies.
- Asserts generated Start_NetworkRecon.ps1 uses scalar variables and passes -u as a separate argument.
- Asserts generated Start_NetworkRecon.cmd sets PYTHONUNBUFFERED=1 and uses -u.
- Rejects the broken comma-separated array syntax from PHASE-068.

TESTS ADDED:
tests/test_build_portable.py::test_embedded_build_generates_launchers_with_unbuffered_flags
- Replaces test_embedded_build_powershell_launcher_passes_u_separately and test_embedded_build_cmd_launcher_keeps_unbuffered_flags.

DDR UPDATES:
UNCHANGED DD:[2026-09-03]

RISKS INTRODUCED:
- None expected; test-only change.

RISKS RESOLVED:
- Regression tests now protect the real launcher generation path rather than duplicated expected text.
- Packaged build is now traceable to a clean committed HEAD.

OPEN ISSUES:
- None.
