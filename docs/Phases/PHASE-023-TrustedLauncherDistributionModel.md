PHASE:
TrustedLauncherDistributionModel

FILES:
build_portable.py
docs/HOWTO-PORTABLE.md
README.md

ACCEPTANCE CRITERIA:
- ZIP distribution's primary entry point is a double-click .cmd/.ps1 launcher, not NetworkDeviceDiagnostics.exe.
- Launcher invokes source app/cli.py via system/bootstrap-resolved Python; no compiled PE executable is required to start the tool.
- README/HOWTO document that this model avoids Defender ASR Rule 01443614 (blocks low-prevalence PE executables), citing the <CUSTOMER> field test.
- Engineer workflow remains extract -> double-click launcher -> enter details -> collect, with no visible Python/repo knowledge required.
- Existing 64 tests continue to pass; no changes to app/cli.py collection logic.

CONSTRAINTS:
- Reuse PHASE-016 bootstrap Python-discovery logic; no new dependencies.
- Retain existing PyInstaller .exe build as an optional/secondary artifact only.
- Do not implement code-signing or MSIX.

KNOWN RISKS:
- Endpoints without any discoverable Python (per PHASE-016 bootstrap) still cannot launch; this is a pre-existing constraint, not new.
- .cmd/.ps1 launchers can still be blocked by unrelated script-execution policies (e.g., PowerShell execution policy, macro/script ASR rules) on some estates; this needs field validation.

OUTSTANDING RISKS:
- Confirmed in production: unsigned PyInstaller .exe is blocked by ASR Rule 01443614 on managed endpoints (`<CUSTOMER>`).
- Interactive prompts require a TTY; automated runs must use --config (carried).

OPEN QUESTIONS:
- Does the target enterprise's ASR/script-control policy also restrict .ps1/.cmd execution? Requires a second field test before this model is declared sufficient.
