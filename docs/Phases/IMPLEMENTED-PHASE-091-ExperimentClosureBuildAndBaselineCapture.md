# IMPLEMENTED-PHASE-091-ExperimentClosureBuildAndBaselineCapture

Date: 2026-09-10
Agent: Astra (executed by Codex)
Status: Implemented and validated; build/packaging only, no product changes.

## Baseline capture

- Original repository: clean tracked/untracked working tree; HEAD `68b4dad94ac91cbcce7a5233b5c5b7244794f64b` (`Experiment Complete 2026-09-08`). Refreshed origin/master matches that baseline before documentation changes.
- Reviewed PHASE-087/087A implementation is already committed. No merge, remediation, feature, backlog or continuation work was needed.
- Built from a separate local, detached checkout of this exact commit using the unchanged default `python -m build_portable` embedded-runtime path. This is disposable build isolation, not a continuation repository. Existing historical archives were preserved.
- The established 38-file source/test fingerprint in EXPERIMENT-CLOSURE.md is `a612766725791f703a07b949ea2b724b97f86069dd3acef8eab82572caa46d65`. A fresh Windows Git checkout has fingerprint `353eb07d11fca14516d800b8dd5b536141abbedf68a6602de41b2b0cff3601fc`; direct comparison established that the only differences are line endings in three files. The final build uses the clean Git checkout, and its packaged application files were compared byte-for-byte against that checkout.
- A preliminary package created during the line-ending check recorded `dirty=true` with no content patch. It was replaced by a fresh clean build, not edited or relabelled. Only the clean build below is delivered.

## Final archive

| Property | Verified value |
|---|---|
| Archive filename | `NetworkReconEngine-PHASE-091.zip` |
| Repository-local location | `dist/NetworkReconEngine-PHASE-091.zip` |
| Build source commit | `68b4dad94ac91cbcce7a5233b5c5b7244794f64b` |
| Build timestamp | `2026-09-10T13:48:09.491970+00:00` (14:48:09 BST) |
| Archive SHA-256 | `26fb460aa6264b18231b5dc896426ec998de61489d9729c2ef9b4a4a324d366e` |
| Archive size | `21,179,113` bytes |
| Archive members | `1,874` |
| Embedded Python | CPython `3.12.10`, Windows x64 |
| Build mode | Default embedded runtime; modern requirements; no legacy/PyInstaller mode |

The unchanged builder outputs `NetworkReconEngine.zip` in the isolated checkout. Copying it to the phase-specific delivery filename preserves the exact bytes and SHA-256. This archive includes the reviewed PHASE-087/087A code and supersedes PHASE-085 for the final experiment build. Historical artefacts remain historical.

## Validation

- `py_compile`: **40 files passed** (20 application, 18 test, 2 root Python files), including a pass using the embedded Python interpreter.
- Full pytest suite with the established dependency environment: **354 passed, 1 warning**.
- Full pytest suite with the fresh embedded Python and its installed dependency set: **354 passed, 1 warning** in 2.28 seconds. Final package dependencies exactly match this tested environment.
- The warning is the existing deliberate generic-profile fallback test for an unknown vendor/platform.
- Environment qualifications: a fresh checkout omits ignored `config/devices.yml`; an initial run had 13 missing-file failures (341 passed). A synthetic ignored inventory supplied this existing suite prerequisite. No production credentials were copied and no test/application code changed.
- Running tests directly beside package metadata initially produced 2 provenance-test failures (352 passed): those tests explicitly expect metadata to be absent. Running an identical copy of the embedded interpreter/dependencies outside the bundle metadata restored their intended test environment. Actual metadata fallback was tested separately through both launchers below.

Repeatable validation uses a fresh test directory and the existing `pytest -q -o addopts= --basetemp <fresh-path>` invocation. Compilation writes caches outside application staging. The isolated checkout remained Git-clean at final build time.

## Provenance, extraction and launchers

- Both `build_manifest.json` and `build_runtime_provenance.json` are present in the ZIP root.
- Manifest `commit_sha` equals runtime `head_commit_sha`, both matching the exact build commit above.
- Both record `dirty: "false"`, empty `patch_checksum`, and `excluded_paths: "config/*.yml"`. Runtime `patch` is empty. This agrees with the inspected build checkout.
- ZIP CRC verification passed for the complete archive. Member paths were checked to remain within a fresh extraction directory; every extracted file matched its archive content.
- All 20 packaged application `.py` files, `run_portable.py` and `requirements.txt` match the clean build source byte-for-byte.
- `Start_NetworkRecon.cmd`: `--help` and an external-working-directory synthetic `--dry-run --verbose` both returned success.
- `Start_NetworkRecon.ps1`: the same two checks returned success.
- Both launchers invoke the bundled interpreter and forward arguments. No installed Python is needed for these checks.
- Git was deliberately unavailable on PATH throughout both dry runs. Each emitted `build_provenance.json` with the expected commit, `dirty=false` and no patch, establishing packaged runtime fallback.
- Both dry runs produced a successful seed summary, device ZIP, manifest, topology and console log. No live SSH session or field collection was performed.

## Configuration hygiene

- Packaged configuration consists of exactly `config/devices.yml.example` and `config/interactive_devices.yml.example`, byte-identical to tracked templates.
- No live `.yml` configuration, synthetic test inventory, `.git`, `.venv`, raw field captures, tests or collection output was packaged.
- No application bytecode/cache directories were staged.
- Empty provenance patches prevent tracked-diff content from entering this clean package. This is a bounded package-hygiene verification, not clearance of repository history for public publication.

## Installed dependency record

Resolved by the unchanged minimum-version requirements on build date:

```text
asyncssh==2.24.0
bcrypt==5.0.0
cffi==2.1.1
colorama==0.4.6
cryptography==50.0.1
iniconfig==2.3.0
invoke==3.0.3
markdown-it-py==4.2.0
mdurl==0.1.2
packaging==26.3
paramiko==5.0.0
pluggy==1.6.0
pycparser==3.0
Pygments==2.21.0
PyNaCl==1.6.2
pytest==9.1.1
PyYAML==6.0.3
rich==15.0.0
typing_extensions==4.16.0
```

These versions record this artefact; no dependency files were changed or new reproducibility guarantees introduced.

## Files and commit boundary

- Created: `docs/Phases/IMPLEMENTED-PHASE-091-ExperimentClosureBuildAndBaselineCapture.md`.
- Updated append-only: `docs/PROJECT-JOURNAL.md`.
- Created ignored build deliverable: `dist/NetworkReconEngine-PHASE-091.zip`.
- These documentation changes are committed and pushed under the user-authorised message `Final Experiment Release`. The documentation commit follows the build source commit; it is not the source SHA embedded in the archive. Successful push is verified operationally against origin/master.
- ZIPs remain ignored under the existing policy. The archive is supplied locally, not force-added to Git or uploaded as a hosted release. No tag, archive-status change or continuation operation is included.
- PHASE-090's statements that no new package was produced describe its historical execution; PHASE-091 supplies that package now.

## Handover

```text
PHASE:
PHASE-091-ExperimentClosureBuildAndBaselineCapture
FILES:
Implementation record; append-only journal; ignored phase-specific ZIP.
ACCEPTANCE CRITERIA:
Fresh attributable build; compilation/full suite; matching clean provenance;
extraction, launchers and config checks; documentation commit/push.
CONSTRAINTS:
No application/test changes, remediation, features or continuation work.
KNOWN RISKS:
Minimum-version dependencies; narrow field coverage; restricted history.
OUTSTANDING RISKS:
No new live field validation or production-readiness claim.
OPEN QUESTIONS:
None blocking PHASE-091 completion.
```

UNCHANGED DD:2026-09-08
