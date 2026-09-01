REVIEW VERDICT:
Not Approved

CRITICAL ISSUES:
Issue:
`--max-concurrent 0` or a negative value causes the parallel queue loop to make no progress.

Why It Matters:
The CLI accepts these values; `while len(wave) < max_concurrent` creates an empty wave while queue remains non-empty, so a scoped run hangs and no checkpoint is emitted.

Recommended Fix:
Reject non-positive CLI values or normalize them to one before the wave loop.

Issue:
A parallel wave can collect more than `max_devices` permits.

Why It Matters:
The loop checks the limit before building a wave but does not restrict wave size to the remaining capacity, so a final wave can exceed the established collection limit.

Recommended Fix:
Limit each wave to `min(max_concurrent, max_devices - len(visited))`.

MAJOR ISSUES:
None

DDR REVIEW:
Decision ID: DD-005

Approved

OUTSTANDING RISKS:
- Cross-workstation bootstrap validation remains pending.
- `--max-concurrent` has no upper ceiling and can stress AAA services.

OPEN QUESTIONS:
- Should `--max-concurrent` have an enforced upper ceiling?

RECOMMENDED NEXT PHASE:
PHASE-018A-ParallelScopedCollectionRemediation
