PHASE:
PHASE-060-PortableBuildPackagingAndProvenanceHygiene

STATUS:
Implemented

FILES MODIFIED:
- build_portable.py
- tests/test_build_portable.py
- docs/Phases/PHASE-060-PortableBuildPackagingAndProvenanceHygiene.md
- docs/Phases/IMPLEMENTED-PHASE-060-PortableBuildPackagingAndProvenanceHygiene.md

CHANGES:
- build_portable.py now copies only config/*.yml.example files into the embedded bundle, avoiding local credential-bearing config/*.yml files.
- build_portable.py writes build_manifest.json at build time, using app/provenance.py to capture commit SHA, dirty flag, and patch checksum; this makes the bundle self-describing even without .git at runtime.
- tests/test_build_portable.py updated to verify manifest generation and config hygiene.

VALIDATION:
- `python -m py_compile build_portable.py tests/test_build_portable.py` passed.
- `pytest tests/test_build_portable.py -v` passed.
- `pytest` full suite passed.
- Fresh embedded build generated successfully; archive inspection confirmed devices.yml and interactive_devices.yml are absent, example templates are present, build_manifest.json is present and contains expected metadata.

DDR UPDATES:
UNCHANGED DD:DD-015

RISKS INTRODUCED:
- Operators must provide local config files on first run when using a portable build; only templates are included.

RISKS RESOLVED:
- Portable builds no longer risk distributing local credentials.
- Portable builds now carry durable build provenance so field evidence can be tied back to a specific source build.

OPEN ISSUES:
- None.
