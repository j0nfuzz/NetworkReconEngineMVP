PHASE:
EmbeddedPythonRuntimeDistribution

STATUS:
Implemented

FILES MODIFIED:
- build_portable.py
  - Added default embedded-runtime build mode.
  - Downloads the official CPython 3.12.10 embeddable ZIP from python.org.
  - Installs pip and project dependencies into the bundled runtime.
  - Stages app/, config/, run_portable.py, requirements.txt, and launcher scripts.
  - Produces dist\NetworkReconEngine.zip as the primary distribution artifact.
  - Retained --pyinstaller flag for the legacy PyInstaller executable build.
- run_portable.py
  - Added bundle-root path insertion so the embedded interpreter can locate app/.
- README.md
  - Documented embedded-runtime bundle as the recommended managed-endpoint distribution.
  - Added <CUSTOMER> field-test evidence and ASR Rule 01443614 rationale.
  - Moved PyInstaller executable guidance to a legacy section.
- docs/HOWTO-PORTABLE.md
  - Documented the embedded-runtime bundle workflow and archive contents.
  - Added ASR Rule 01443614 field-test explanation.
  - Moved PyInstaller executable guidance to a legacy section.

FILES ADDED:
- docs/Phases/IMPLEMENTED-PHASE-024-EmbeddedPythonRuntimeDistribution.md

VALIDATION EVIDENCE:
- pytest: 146 passed.
- build_portable.py produced dist\NetworkReconEngine.zip (~29 MB) containing python.exe, app/, config/, Start_NetworkRecon.cmd, Start_NetworkRecon.ps1, and dependencies.
- Extracted bundle launched successfully via bundled python.exe run_portable.py --help.
- Extracted bundle launched successfully via Start_NetworkRecon.cmd --help.
- No interactive_devices_*.yml temp files remained after validation.

TESTS ADDED:
- None (distribution build only).

DDR UPDATES:
UNCHANGED DD:DD-005

RISKS INTRODUCED:
- ZIP size is materially larger than the PyInstaller package (embedded interpreter + dependencies).
- Embeddable runtime must be kept in sync with the project's Python 3.12+ requirement.
- Whether the embedded python.exe avoids ASR blocking on all managed estates requires further field validation; <CUSTOMER> proved scripts are allowed but the embedded runtime itself was not field-tested.

RISKS RESOLVED:
- Distribution no longer depends on a system Python installation.
- Default distribution avoids low-prevalence PyInstaller executables blocked by Defender ASR Rule 01443614.

OPEN ISSUES:
- Field-test the bundled python.exe on the <CUSTOMER> endpoint to confirm it is not also blocked by ASR or other trust controls.
