PHASE:
PublicReleaseSanitisation

FILES:
README.md
docs/HOWTO-PORTABLE.md
docs/PROJECT-JOURNAL.md
docs/Phases/PHASE-023-ScriptBasedLaunchForManagedEndpoints.md
docs/Phases/PHASE-023-TrustedLauncherDistributionModel.md
docs/Phases/PHASE-024-EmbeddedPythonRuntimeDistribution.md
docs/Phases/IMPLEMENTED-PHASE-024-EmbeddedPythonRuntimeDistribution.md
NetworkDeviceDiagnostics.spec
.gitignore

ACCEPTANCE CRITERIA:
- No occurrence of "Sapphire" remains anywhere in tracked files; replaced with a neutral placeholder (e.g., "`<CUSTOMER>`") preserving the technical meaning of the field-test evidence.
- NetworkDeviceDiagnostics.spec contains no employer name, personal name, or absolute local user path.
- NetworkRecon.zip and test_bootstrap/ are removed from git tracking (git rm --cached) and added to .gitignore.
- Existing 146 tests continue to pass; no application logic changed.

CONSTRAINTS:
- Preserve technical meaning of all field-test narratives (ASR Rule ID, Event ID, behavior described) — only the tenant/customer name changes.
- Do not alter PROJECT-JOURNAL.md historical entries beyond the identifier substitution (append-only principle; substitution is a correction, not a rewrite of findings).
- Do not attempt to rewrite git history in this phase.

KNOWN RISKS:
- Regenerating NetworkDeviceDiagnostics.spec via PyInstaller may reformat unrelated fields; prefer a minimal text edit of the pathex/analysis path only.
- Removing tracked binaries changes repository size/history only from this commit forward; prior commits still contain them until history is rewritten.

OUTSTANDING RISKS:
- Git commit history still contains the real employer email/name across ~180 files' history; this must be resolved via git filter-repo (or equivalent) before the remote is made public. This is a hard release blocker not addressed by this phase.

OPEN QUESTIONS:
- Should the neutral placeholder tenant name also be applied retroactively to closed PHASE-023/024 review artefacts, or left as historical record with a substitution note? Recommend substitution for public release given PROJECT-STANDARD's append-only intent still permits correcting identifiable-information errors.
