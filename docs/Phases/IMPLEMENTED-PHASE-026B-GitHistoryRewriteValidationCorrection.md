PHASE:
GitHistoryRewriteValidationCorrection

STATUS:
Implemented

FILES MODIFIED:
- docs/Phases/IMPLEMENTED-PHASE-026-GitHistoryAuthorSanitisation.md
  - Rewrote Step 3 validation to compare pre-rewrite commits from the `pre-mailmap-rewrite` tag against post-rewrite `master` commits via `.git/filter-repo/commit-map`.
  - Pre-rewrite commit IDs are captured as `..\before-rewrite-ids.txt` before `git filter-repo` runs.
  - Post-rewrite commit IDs are read from `git log master --format="%H"`.
  - For every old/new mapped pair the script validates:
    - mapped new commit exists
    - order matches the post-rewrite master sequence
    - author date (%at) is identical
    - commit message body (%B) is identical
    - tree hash (%T) is identical
  - Identity check scans only the rewritten `master` branch.
  - Validation failure stops execution before Step 4 (force-push).

TESTS ADDED:
- None (documentation-only change; no application code or repository state modified).

DDR UPDATES:
UNCHANGED DD:DD-005

RISKS INTRODUCED:
- None. The rewrite itself has still not been executed.

RISKS RESOLVED:
- REVIEW-PHASE-026A's finding that the validation used post-rewrite history for both before and after lists is corrected; old IDs are now explicitly mapped to new IDs and compared.

OPEN ISSUES:
- The `git filter-repo` rewrite remains to be executed by the repository owner.
- Force-push remains pending owner confirmation and successful validation.
