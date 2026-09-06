PHASE:
PHASE-068B-LauncherRegressionAndCheckpointClosure

FILES:
tests/test_build_portable.py

ACCEPTANCE CRITERIA:
- Tests invoke build_portable._build_embedded() directly and assert on its actual generated launcher output.
- Tests validate Start_NetworkRecon.ps1 passes -u and run_portable.py as separate arguments.
- Tests validate Start_NetworkRecon.cmd sets PYTHONUNBUFFERED=1 and uses -u.
- Fresh portable build generated from a clean committed HEAD reports dirty: false and commit_sha matching HEAD.
- Extracted Start_NetworkRecon.ps1 executes --help successfully from the traceable build.
- Full pytest suite passes.

CONSTRAINTS:
- No production launcher-generation changes unless a genuine defect is discovered.
- No run_portable.py, cli.py, or orchestrator.py changes.
- No PHASE-069 work.
- Keep the change small and reviewable.

KNOWN RISKS:
- Mocking network downloads and subprocess installs in tests may mask future real build failures.

OUTSTANDING RISKS:
- None beyond DD-011 (unchanged).

OPEN QUESTIONS:
- None.
