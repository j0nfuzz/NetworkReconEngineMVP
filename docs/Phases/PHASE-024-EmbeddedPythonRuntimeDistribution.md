PHASE:
EmbeddedPythonRuntimeDistribution

FILES:
build_portable.py
docs/HOWTO-PORTABLE.md
README.md

ACCEPTANCE CRITERIA:
- Distributed ZIP contains the official CPython embeddable runtime (unmodified python.exe/pythonXY.dll) plus app/ source and installed dependencies, with no system Python or venv required.
- A .cmd/.ps1 launcher invokes the bundled python.exe against app/cli.py directly; no PyInstaller-built .exe is required for the default workflow.
- README/HOWTO document that the embeddable runtime is Microsoft's official unmodified binary, chosen specifically because it does not carry the low-prevalence signature that triggers ASR Rule 01443614 (`<CUSTOMER>` evidence).
- Engineer workflow remains extract -> double-click launcher -> enter details -> collect, with no Python install, admin rights, or venv step.
- Existing 64 tests continue to pass; no changes to app/cli.py collection logic.

CONSTRAINTS:
- Use the official python.org embeddable ZIP for the project's supported Python version; do not hand-build or modify the interpreter binary.
- Dependencies (pyyaml, paramiko, asyncssh, etc.) must be pip-installed into the bundled runtime's site-packages at build time, not requiring network access at runtime.
- Do not implement code-signing or MSIX.
- Bundled runtime download/build step must be reproducible and documented in build_portable.py.

KNOWN RISKS:
- Embeddable Python distributions disable some stdlib features (e.g., site module, pip) by default; build script must enable site-packages via python._pth edits.
- ZIP size increases materially (bundled interpreter + dependencies) versus current onedir package.
- Embeddable runtime version must be kept in sync with the project's minimum Python requirement (3.12+).

OUTSTANDING RISKS:
- Confirmed in production: unsigned PyInstaller .exe blocked by ASR Rule 01443614; script execution is allowed (`<CUSTOMER>`).
- Interactive prompts require a TTY; automated runs must use --config (carried).

OPEN QUESTIONS:
- Does the embeddable python.exe itself carry sufficient Microsoft-signed prevalence to avoid ASR blocking on all managed estates, or only `<CUSTOMER>`? Requires a second field test after implementation.
