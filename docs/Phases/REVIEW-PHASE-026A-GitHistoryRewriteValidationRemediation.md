# REVIEW-PHASE-026A-GitHistoryRewriteValidationRemediation

REVIEW VERDICT:

Not Approved

CRITICAL ISSUES:

None

MAJOR ISSUES:

Issue:
The Step 3 script derives both `$beforeList` and `$afterList` from post-rewrite `git log --all`; the captured pre-rewrite list is used only for a count.

Why It Matters:
The map lookup receives rewritten IDs instead of old IDs and cannot prove mapped-pair order, chronology, messages, or trees; `--all` can also include the pre-rewrite tag, making its count/order unsuitable.

Recommended Fix:
Read the pre-rewrite commit IDs from the pre-rewrite capture or `pre-mailmap-rewrite`, read rewritten IDs from `HEAD` only, and compare their mapped pairs in a fixed single-ref order.

DDR REVIEW:

UNCHANGED DD:DD-005

OUTSTANDING RISKS:

- Raw author/committer metadata remains unsanitised until the owner-approved rewrite succeeds.

OPEN QUESTIONS:

None

RECOMMENDED NEXT PHASE:

PHASE-026B-GitHistoryRewriteValidationCorrection