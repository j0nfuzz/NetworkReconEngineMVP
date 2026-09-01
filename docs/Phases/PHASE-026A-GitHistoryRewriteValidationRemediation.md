PHASE:
GitHistoryRewriteValidationRemediation

FILES:
docs/Phases/IMPLEMENTED-PHASE-026-GitHistoryAuthorSanitisation.md

ACCEPTANCE CRITERIA:
- Execution plan defines a per-commit validation step comparing every pre-rewrite commit to its mapped post-rewrite commit.
- Validation proves, for every commit pair: identical chronology order, identical commit message (subject+body), and identical tree hash.
- Validation is deterministic and scriptable (no manual sampling of "several SHAs").
- Validation runs after Step 2 (filter-repo) and before Step 4 (force-push), gating push on a pass result.
- No change to the mailmap mapping, the use of git filter-repo, or the rewrite itself.

CONSTRAINTS:
- Edit only the execution-plan/validation section of IMPLEMENTED-PHASE-026-GitHistoryAuthorSanitisation.md.
- Do not modify .mailmap, PHASE-026-GitHistoryAuthorSanitisation.md, or any application code.
- Do not execute git filter-repo or any destructive/history-rewriting command.
- Do not perform or simulate a force-push.
- Use only standard git plumbing (e.g. git log with --format, tree hashes) callable from PowerShell; no new external dependencies.

KNOWN RISKS:
- filter-repo's own commit ID map file (if generated) is the authoritative old->new mapping; validation must use it rather than assuming commit order alignment.

OUTSTANDING RISKS:
- Raw author/committer metadata remains unsanitised until the owner-approved rewrite is executed (unchanged from PHASE-026).

OPEN QUESTIONS:
- None.
