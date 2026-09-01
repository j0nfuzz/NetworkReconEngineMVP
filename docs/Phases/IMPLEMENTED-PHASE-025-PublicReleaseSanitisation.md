PHASE:
PublicReleaseSanitisation

STATUS:
Implemented

FILES MODIFIED:
- README.md
  - Replaced the real customer/tenant field-test reference with a neutral placeholder name; technical meaning (ASR Rule ID, behavior) unchanged.
- docs/HOWTO-PORTABLE.md
  - Replaced two occurrences of the real customer/tenant field-test reference with a neutral placeholder name.
- docs/PROJECT-JOURNAL.md
  - Replaced three occurrences of the real customer/tenant field-test reference with a neutral placeholder name in existing journal entries.
- docs/Phases/PHASE-023-ScriptBasedLaunchForManagedEndpoints.md
  - Replaced the real customer/tenant field-test reference with a neutral placeholder name.
- docs/Phases/PHASE-023-TrustedLauncherDistributionModel.md
  - Replaced two occurrences of the real customer/tenant field-test reference with a neutral placeholder name.
- docs/Phases/PHASE-024-EmbeddedPythonRuntimeDistribution.md
  - Replaced three occurrences of the real customer/tenant field-test reference with a neutral placeholder name.
- docs/Phases/IMPLEMENTED-PHASE-024-EmbeddedPythonRuntimeDistribution.md
  - Replaced three occurrences of the real customer/tenant field-test reference with a neutral placeholder name.
- NetworkDeviceDiagnostics.spec
  - Replaced the hard-coded local workstation path (containing employer and personal name) with a relative path.
- .gitignore
  - Added test_bootstrap/ and *.zip to prevent tracked binary artefacts and generated test-run output from recurring.

FILES REMOVED FROM TRACKING:
- NetworkRecon.zip
- test_bootstrap/bundle_manifest.json
- test_bootstrap/interactive-device.zip
- test_bootstrap/interactive-device/ai_prompt.txt
- test_bootstrap/interactive-device/summary.json

FILES ADDED:
- docs/Phases/IMPLEMENTED-PHASE-025-PublicReleaseSanitisation.md

VALIDATION EVIDENCE:
- Tenant-identifier scan: no matches (tracked content clean).
- git grep -i "example-employer": no matches (tracked content clean).
- git grep -i "<USERNAME>": no matches (tracked content clean).
- NetworkDeviceDiagnostics.spec Analysis path is now ['run_portable.py'] with no local user path.
- git status confirms NetworkRecon.zip and test_bootstrap/* are staged for deletion from tracking.
- pytest: 146 passed.

TESTS ADDED:
- None (sanitisation-only change; no application logic modified).

DDR UPDATES:
UNCHANGED DD:DD-005

RISKS INTRODUCED:
- None. Untracked artefacts remain on disk locally (git rm --cached only removes them from the index, not the working tree) and must be excluded from any future commit via the updated .gitignore.

RISKS RESOLVED:
- Real customer/tenant field-test identifier no longer present in tracked documentation.
- Employer and personal local workstation path no longer present in the tracked PyInstaller spec file.
- Unnecessary tracked binary artefacts (packaged ZIP, generated test-run output) removed from source control.

OPEN ISSUES:
- Git commit history still contains the real employer email/name in author metadata across prior commits; this is addressed separately by PHASE-026-GitHistoryAuthorSanitisation and is not resolved by this phase.
