REVIEW VERDICT:
Not Approved

CRITICAL ISSUES:
Issue:
Scoped resume re-emits filtered-out checkpoint entries as pending.

Why It Matters:
`queued` is initialized from all persisted pending names before filtering; `state_to_checkpoint()` therefore writes out-of-scope entries back to the checkpoint despite them not being enqueued for collection.

Recommended Fix:
Initialize `queued` from the filtered pending names when `allowed_devices` is active and add an assertion on emitted checkpoint pending state.

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
PHASE-017B-TopologyAwareTroubleshootingScopeCheckpointRemediation
