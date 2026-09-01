REVIEW VERDICT:
Not Approved

CRITICAL ISSUES:
Issue:
`--target-device` does not select the requested configured device as the recursive seed.

Why It Matters:
`main()` always passes `devices[0]`; the orchestrator unconditionally collects that seed, so targeting any non-first device collects an unrelated device and may never collect the requested target.

Recommended Fix:
Resolve the named configured target as the seed before invoking recursive collection and add a non-first-target regression test.

Issue:
Checkpoint `pending` devices are not restricted by `allowed_devices`.

Why It Matters:
Resume reconstruction queues all persisted pending entries before scope filtering, allowing an explicitly scoped run to collect devices outside the target's direct-neighbour scope.

Recommended Fix:
Filter resumed pending entries against the allowed scope without changing the checkpoint format, with a focused resume regression test.

MAJOR ISSUES:
None

DDR REVIEW:
UNCHANGED DD:2026-08-05

OUTSTANDING RISKS:
- Single-hop scoping remains intentionally incomplete for wider fault domains.
- Cross-workstation bootstrap validation remains pending.

OPEN QUESTIONS:
None

RECOMMENDED NEXT PHASE:
PHASE-017A-TopologyAwareTroubleshootingScopeRemediation
