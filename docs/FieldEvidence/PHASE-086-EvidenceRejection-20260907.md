# PHASE-086 Evidence Submission Review — REJECTED (2026-09-07)

> **SUPERSEDED 2026-09-07.** This review incorrectly stated the bundle could not be located and reasoned from documentary inference. The bundle exists at `field_tests/FT060920262050.zip` and has since been extracted and analysed directly. See [PHASE-083-FT060920262050-DirectBundleVerification-20260907.md](PHASE-083-FT060920262050-DirectBundleVerification-20260907.md) for the corrected, evidence-first findings. The substantive technical conclusion below (bundle predates the PHASE-084 fix) is independently confirmed by that direct analysis; the search/process failure that produced this document is not.

## Submission Reviewed

A 2026-09-07 request presented bundle identifier `FT060920262050.zip` with a console-log narrative claiming HOSTNAME-06 completed the 11-command aruba-cx profile successfully, alongside a per-device JSON evidence block claiming `commands_run: 13`, six failed commands, and empty `discovered_neighbors` for the same device in the same run.

## Evidence Assessment

1. **Internal inconsistency**: the submitted narrative (11/11 commands, full success) directly contradicts the submitted JSON evidence (13 commands, 6 failures) for the same device in the same run. Both cannot be true simultaneously.
2. **Bundle identity match**: the identifier `FT060920262050.zip`, the exact six failed AOS-S commands (`show inventory`, `show interfaces brief`, `show lldp neighbors detail`, `show switch info`, `show log buffer`, `show trunks`), the seed's neighbour list (6 LLDP neighbours including `HOSTNAME-01/002/003` and `HOSTNAME-20`), and the seed's misparsed model field (`"2017-2023"`) are byte-for-byte identical to the bundle already dispositioned in `docs/FieldEvidence/PHASE-083-20260906-2050-fieldvalidation-findings.md`, collected against the **PHASE-082 build (commit c290677)** — before the PHASE-084 fix existed.
3. **No PHASE-085 provenance presented**: no `build_provenance.json` head_commit_sha was supplied confirming attribution to the PHASE-085 build (462bf43). No `docs/FieldEvidence/PHASE-086-*.md` findings file existed prior to this review, confirming PHASE-086 has not previously executed.
4. **Plausible mechanism (process, not code)**: PHASE-085's own IMPLEMENTED record records a live hazard — the canonical `dist/NetworkReconEngine.zip` remained locked on the OLDER PHASE-082 build (c290677) at build time, with an explicit instruction that PHASE-086 field deployment MUST use the SHA-verified `dist/NetworkReconEngine-PHASE-085.zip` instead. Deploying the stale canonical archive would reproduce this exact defect signature without any new code fault.

## Root Cause Assessment

No new root cause is established. The defect signature exactly matches the already-diagnosed and already-fixed PHASE-084 root cause (sequential-path identity-probe gate skipped for classification-derived neighbours, causing AOS-Switch profile selection on ArubaOS-CX hardware). This submission provides no evidence that the PHASE-084 fix is ineffective, because it does not carry the provenance required to attribute it to the fixed build.

The reappearance of "HOSTNAME-05" in the traversal narrative cannot be assessed (legitimate neighbour vs. topology/identity-key collapse) without genuine `topology.json`/checkpoint data from a provenance-verified run; this question is deferred to a real PHASE-086 execution.

## MVP Assessment

Unchanged from the PHASE-083/085 disposition: one-hop-out MVP (point at one device → complete, attributed, health-scored package for that device plus a discovered/classified/collected neighbour) remains field-proven. Second-hop traversal (SW3-class discovery) remains unproven. This submission does not move that determination in either direction because it is not valid evidence of the current build.

## Remediation Required?

**No.** No new code defect is proven. The known defect class already has an implemented, reviewed, and packaged fix (PHASE-084, in PHASE-085's artefact). Opening a new remediation phase against unverified/reused evidence would violate evidence-first governance and risk duplicate or contradictory engineering work.

## Disposition

- PHASE-086 status: **NOT EXECUTED**. Remains defined and ready (`docs/Phases/PHASE-086-FieldValidationPost084-SecondHopTraversal.md`), now amended with a mandatory pre-execution provenance gate to prevent this failure mode recurring.
- No DDR change; no source or test change.
- Next genuine field attempt must confirm `build_provenance.json` head_commit_sha == 462bf43 (dirty=false) before any findings are treated as PHASE-086 evidence, and must use a newly-timestamped bundle.
