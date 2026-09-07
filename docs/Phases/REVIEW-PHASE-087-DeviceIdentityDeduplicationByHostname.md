# REVIEW-PHASE-087-DeviceIdentityDeduplicationByHostname

REVIEW VERDICT:

Not Approved

CRITICAL ISSUES:

None.

MAJOR ISSUES:

Issue:
- Alias detection skips recollection but does not record an alias/back-edge to the existing topology node.

Why It Matters:
- `topology.json` continues to emit `HOSTNAME-06 -> HOSTNAME-05` while only `192.168.2.241` is collected as the physical seed node. The edge target is therefore unlinked, and the required physical relationship to the existing node is not represented.

Recommended Fix:
- Preserve the LLDP-reported alias and management address as edge evidence, while resolving the graph target to the already-collected node and recording the alias relationship.

DDR REVIEW:

Decision ID: DD-016

Rejected

Reason:
The implementation prevents collection duplication but does not satisfy the required alias/back-edge topology representation.

OUTSTANDING RISKS:

- Devices whose LLDP-reported management address differs from the originally used management address remain outside this phase's identity check.
- SW3-class third-hop hardware remains unproven by field evidence.

OPEN QUESTIONS:

None.

RECOMMENDED NEXT PHASE:

PHASE-087-TopologyAliasBackEdgeRemediation

VALIDATION ASSESSMENT:

- `py_compile`: passed.
- Targeted suite: 54 passed.
- Full suite: 350 passed, 1 established profile-fallback warning.
- Direct topology reproduction proves the gap: an edge with `target: "HOSTNAME-05"` and `ip: "192.168.2.241"` is emitted while nodes contain `"192.168.2.241"`, not `"HOSTNAME-05"`.

REGRESSION ASSESSMENT:

- Sequential and parallel tests correctly prove redundant collection is prevented and distinct-address devices still collect.
- Coverage does not build/assert `topology.json` for an alias edge, so it cannot detect the unmet back-edge requirement.

CHECKPOINT ASSESSMENT:

- Not stable for push: the phase has an unresolved major acceptance failure and DD-016 is rejected.

CLOSURE RECOMMENDATION:

- Do not close PHASE-087; implement the narrowly scoped topology alias/back-edge remediation and add topology output regression coverage.

PUSH DECISION:
DO NOT PUSH

Reason:
PHASE-087 is Not Approved and DD-016 is rejected because topology identity remains split.
