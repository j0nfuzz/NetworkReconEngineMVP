PHASE:
ArubaOSCXFieldTestBuildPreparation

FILES:
(none — no source or test files are modified in this phase)
Outputs only: dist/NetworkReconEngine.zip (rebuilt), a new git commit containing the already-approved PHASE-047 working-tree changes.

ACCEPTANCE CRITERIA:
- Commit the currently uncommitted PHASE-047 changes (`app/vendor_profiles.py`, `app/collector.py`, `tests/test_vendor_profiles.py`, `tests/test_cli.py`, plus PHASE-047 documentation artefacts) to git with message `PHASE-047: ArubaOS-CX command profile correction`, producing a concrete commit SHA.
- Rebuild `dist/NetworkReconEngine.zip` from that commit using the existing `build_portable.py` (embedded-runtime mode), unmodified.
- Verify the packaged bundle contains the corrected `app/vendor_profiles.py` (the `aruba-cx` profile) by inspecting the built package contents.
- Verify `run_portable.py --help` launches successfully from the built package.
- Verify a dry-run collection against the existing config executes without error using the built package.
- Record the resulting commit SHA and build artifact size/hash in the IMPLEMENTED file so a future field-validation phase can verify it is testing a PHASE-047-or-later build before analysing any evidence.
- Full regression suite passes (`python -m pytest tests -q`) before packaging.

CONSTRAINTS:
- No source code behaviour changes. This phase packages and commits already-approved, already-reviewed work; it does not write new production code.
- Do not modify SSH, retry, timeout, recovery, credential, topology, provenance, or troubleshooting-scope behaviour.
- Do not perform field evidence collection or analysis in this phase.
- Do not run `git push` without explicit user confirmation.
- Do not fabricate or backdate provenance; the build's provenance artifact must reflect the real new commit SHA.

KNOWN RISKS:
- None beyond standard packaging risk; `build_portable.py` is an existing, previously-used script.

OUTSTANDING RISKS:
- ArubaOS-CX remediation (PHASE-047) remains unvalidated on real hardware until a future field-validation phase uses this new build against a reachable device (carried from PHASE-048).
- DD-007 remains inconclusively validated on real hardware (unrelated, carried risk).

OPEN QUESTIONS:
- None. This phase is a prerequisite mechanical step; the next field-validation attempt is deferred to a subsequent phase once a reachable ArubaOS-CX device is available.
