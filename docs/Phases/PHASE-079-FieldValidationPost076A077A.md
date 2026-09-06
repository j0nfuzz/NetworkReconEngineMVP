PHASE:
PHASE-079-FieldValidationPost076A077A

STATUS:
Executed and closed by evidence

PURPOSE:
Field-validate the PHASE-078 build (commit 1bcd549) covering PHASE-076A portable runtime provenance and PHASE-077A scoped streaming, per the field objectives recorded in REVIEW-PHASE-078.

FILES:
- None (evidence-collection phase; no source or test changes)

EXECUTION EVIDENCE:
- Field bundle: FT060920261933.zip, generated 2026-09-06T18:28:50Z against the PHASE-078 build.
- Findings document: docs/FieldEvidence/PHASE-079-20260906-182850-fieldvalidation-findings.md

ACCEPTANCE OUTCOMES:
- Portable provenance attribution: PROVEN (both device bundles record head_commit_sha 1bcd549..., dirty false; PHASE-075 "unknown" failure mode eliminated).
- Live per-device artefacts and console capture: PROVEN (console.log contains per-device Starting/Finished lines and the final manifest message).
- Topology neighbour identity/IP retention: PROVEN (5 of 6 neighbour records carry their own distinct IPs; topology.json nodes include neighbor_addresses).
- Classification/queueing/attempt of a real neighbour: PROVEN (HOSTNAME-06 classified aruba, queued, attempted).
- DEFECT 1: no intra-device progress output during long silent periods (acceptance gap against operator observability expectations) - dispositioned to PHASE-081.
- DEFECT 2: neighbour credentials not propagated on the interactive journey (empty default credentials block) causing HOSTNAME-06 "Authentication failed." - dispositioned to PHASE-080.

CONSTRAINTS:
- FIELDTEST.MD sanitisation applied throughout the findings document.

KNOWN RISKS:
- None introduced (no code changed).

OUTSTANDING RISKS:
- HOSTNAME-06 branch remains uncollected until PHASE-080 lands and a new field run re-attempts it.
- Ubiquiti/Netgear neighbour support remains intentionally out of scope.
- Empty-credential auth attempts create failed-login noise in target device logs (mitigated by PHASE-080).

OPEN QUESTIONS:
- None; engineering follow-ups are PHASE-080 and PHASE-081.
