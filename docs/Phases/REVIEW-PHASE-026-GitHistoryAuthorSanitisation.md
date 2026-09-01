# REVIEW-PHASE-026-GitHistoryAuthorSanitisation

REVIEW VERDICT:

Not Approved

CRITICAL ISSUES:

None

MAJOR ISSUES:

Issue:
The execution plan validates only the final branch-tip tree with `git diff pre-mailmap-rewrite HEAD`; it does not verify tree identity for every rewritten commit.

Why It Matters:
An intermediate commit could be changed, dropped, or reordered while the final tree remains identical, violating the phase preservation criterion without detection before force-push.

Recommended Fix:
Add a deterministic pre/post commit-map validation that compares every old commit to its mapped rewritten commit for chronology, subject, and tree ID before permitting a force-push.

DDR REVIEW:

UNCHANGED DD:DD-005

OUTSTANDING RISKS:

- The raw author and committer metadata remains unsanitised until the owner-approved rewrite succeeds.

OPEN QUESTIONS:

None

RECOMMENDED NEXT PHASE:

PHASE-026-GitHistoryAuthorSanitisationRemediation