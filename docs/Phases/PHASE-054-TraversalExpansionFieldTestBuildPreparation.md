PHASE:
TraversalExpansionFieldTestBuildPreparation

FILES:
(none — no source or test files are modified in this phase)
Outputs only: dist/NetworkReconEngine.zip (rebuilt), a new git commit containing the already-approved PHASE-052/PHASE-053 working-tree changes.

ACCEPTANCE CRITERIA:
- Commit the currently uncommitted PHASE-052/PHASE-053 changes (`app/cli.py`, `app/parallel_collector.py`, `tests/test_cli.py`, `tests/test_scope.py`, `tests/test_parallel_collector.py`, plus PHASE-052/053 documentation artefacts) to git with message `PHASE-053: remediate automatic traversal root expansion`, producing a concrete commit SHA.
- Rebuild `dist/NetworkReconEngine.zip` from that commit using the existing `build_portable.py` (embedded-runtime mode), unmodified.
- Verify the packaged bundle contains the corrected `app/cli.py` (default-recursion, `--no-recurse`, target-device-as-root) and `app/parallel_collector.py` (`allowed_devices=None` unbounded discovery) by inspecting the built package contents.
- Verify `run_portable.py --help` documents `--no-recurse` and the updated `--target-device`/`--recursive` help text.
- Verify a dry-run collection against the existing config executes without error using the built package.
- Verify a dry-run collection with `--target-device` and no pre-existing `topology.json` executes without error using the built package (exercises the new no-topology traversal-root code path without live SSH).
- Record the resulting commit SHA and build artifact size/hash in the IMPLEMENTED file so a future field-validation phase can verify it is testing a PHASE-053-or-later build before analysing any evidence.
- Full regression suite passes (`python -m pytest tests -q`) before packaging.

CONSTRAINTS:
- No source code behaviour changes. This phase packages and commits already-approved, already-reviewed work; it does not write new production code.
- Do not modify SSH, retry, timeout, recovery, credential, topology, provenance, running-config, or command-profile behaviour.
- Do not perform field evidence collection or analysis in this phase.
- Do not run `git push` without explicit user confirmation.
- Do not fabricate or backdate provenance; the build's provenance artifact must reflect the real new commit SHA.

KNOWN RISKS:
- None beyond standard packaging risk; `build_portable.py` is an existing, previously-used script.

OUTSTANDING RISKS:
- PHASE-052/053's default-recursion and unbounded no-topology neighbour expansion remain unvalidated on real multi-hop hardware until a future field-validation phase uses this new build against a reachable device with real discoverable neighbours.
- Running-config output completeness remains unverified (carried from PHASE-050; tracked separately as RunningConfigCaptureCompletenessValidation).
- ArubaOS-CX command coverage expansion remains deferred pending further field evidence (carried from PHASE-050, unrelated).
- DD-007 remains inconclusively validated on real hardware (unrelated, carried risk).

OPEN QUESTIONS:
- None. This phase is a prerequisite mechanical step; the next field-validation attempt is deferred to a subsequent phase once a reachable multi-hop-capable device is available.
