PHASE:
PortableBuildPackagingAndProvenanceHygiene

FILES:
build_portable.py
tests/test_build_portable.py

ACCEPTANCE CRITERIA:
- Portable embedded builds exclude non-template config/*.yml files (e.g. devices.yml, interactive_devices.yml).
- Only safe *.yml.example template config files are packaged.
- build_manifest.json is generated at build time and embedded in the bundle root.
- Manifest contains commit SHA, dirty flag, build timestamp, and provenance patch checksum when available.
- A portable build remains launchable and functional after the changes.
- Tests verify packaged config hygiene and manifest presence/content.

CONSTRAINTS:
- No changes to discovery, parsers, collectors, orchestrators, vendor profiles, or health scoring.
- No changes to runtime provenance logic unless strictly required to read the embedded manifest.
- No field validation or unrelated build refactoring.

KNOWN RISKS:
- Build script must not accidentally strip config files required for first-run operation.

OUTSTANDING RISKS:
- Legacy PyInstaller path is not the primary field-validation build target; this phase focuses on the embedded bundle.

OPEN QUESTIONS:
- None.
