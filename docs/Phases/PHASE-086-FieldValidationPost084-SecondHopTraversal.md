PHASE:
PHASE-086-FieldValidationPost084-SecondHopTraversal

STATUS:
EXECUTED AND CLOSED BY EVIDENCE (2026-09-07). Bundle field_tests/FT070920261340.zip, both device provenances head_commit_sha 462bf4366d0121b17209856059df9258bc428309 (dirty=false) — genuine PHASE-085 build attribution, directly verified. Findings: docs/FieldEvidence/PHASE-086-20260907-1340-secondhop-findings.md.

RESULT SUMMARY:
- PHASE-084 fix CONFIRMED working: HOSTNAME-06 now receives the identity probe, resolves platform=arubaos-cx, runs the correct 11-command profile, and its LLDP capture succeeds (4/4 neighbours parsed, zero failed commands).
- SW3 (a third downstream switch) does not exist in HOSTNAME-06's LLDP evidence — its only switch-class neighbour is a LAG link back to the seed. Not a discovery/parsing/classification/queueing defect.
- NEW defect discovered: the seed (192.168.2.241) and a neighbour named HOSTNAME-05 are the same physical device (identical hostname, identical neighbour list, identical LLDP-reported identity), but are dequeued as two distinct devices because traversal deduplicates by device.name only, with no hostname/IP identity cross-check. Dispositioned to PHASE-087-DeviceIdentityDeduplicationByHostname.
- MVP achieved: seed -> correctly-profiled, fully-collected real second-hop device, with complete usable artefacts.

MANDATORY PRE-EXECUTION GATE (satisfied by this run):
- Before any findings document is written, extract build_provenance.json from the collected bundle and confirm head_commit_sha == 462bf4366d0121b17209856059df9258bc428309 (the PHASE-085 build) with dirty=false. If the commit SHA is c290677... (PHASE-082) or "unknown", the bundle is INVALID for this phase — do not analyze further; re-deploy using the SHA-verified dist/NetworkReconEngine-PHASE-085.zip (SHA-256 776B2527A1840C301EBB3074741EC1509FF2E50C138255365EE9F852E16BFC30) and re-collect.
- Confirm the field-test bundle filename/timestamp corresponds to a new collection event, not a reused prior artefact.

FILES:
- None (evidence-collection phase; no source or test changes)
- Outputs: docs/FieldEvidence/PHASE-086-<timestamp>-secondhop-findings.md

PURPOSE:
Field-validate the PHASE-085 build against the same ArubaOS-CX infrastructure that produced FT060920262050, targeting the exact defect chain PHASE-084 closed plus second-hop traversal.

EXECUTION PROCEDURE:
1. Deploy the PHASE-085 bundle (recorded archive SHA) per FIELDTEST.MD.
2. Interactive recursive run against the seed device (default journey).
3. Confirm and record:
   - console.log shows identity-probe lines for the HOSTNAME-06-class neighbour ("probing identity..." then "identity resolved: vendor=aruba" with the aruba-cx command count (11) visible in the (i/N) stream, NOT 13);
   - HOSTNAME-06 summary.json records platform arubaos-cx and identity_confidence > 0;
   - HOSTNAME-06 failed_commands is empty or materially reduced (expected: none of the six AOS-S verbs reappear); show lldp neighbor-info detail captured with real LLDP data;
   - discovered_neighbors for HOSTNAME-06 is non-empty, including the previously-missing downstream switch (SW3 class);
   - topology.json contains multi-hop structure (seed -> HOSTNAME-06 -> downstream) with each neighbour retaining its own address in neighbor_addresses/edges;
   - recursion attempts classification-supported downstream switches; AP-class neighbours (no CLI) land cleanly in failed/unsupported without retry churn;
   - bundle build_provenance.json head_commit_sha equals the PHASE-085 build HEAD (never "unknown");
   - health scoring penalises any partial device (PHASE-057 behaviour).
4. Sanitise all findings per FIELDTEST.MD; classify each observation as supported/disproven/inconclusive.

ACCEPTANCE CRITERIA:
- Evidence findings document created with per-item verdicts against the list above.
- If no reachable devices are available, record "blocked - no reachable device" per PHASE-040/046/048 precedent (acceptable outcome, not failure).
- No source changes regardless of outcome; defects disposition to new remediation phases only.

CONSTRAINTS:
- Read-only collection commands only; FIELDTEST.MD handling throughout.

KNOWN RISKS:
- Field access availability; downstream device credential correctness (propagated defaults must be valid on discovered devices); AP-class neighbours will attempt SSH and fail by design.

OUTSTANDING RISKS:
- Third-hop expansion beyond the first downstream layer remains unproven by any prior evidence.

OPEN QUESTIONS:
- Whether LLDP System-Description on downstream switches yields correct vendor classification for non-Aruba devices (first real multi-vendor classification evidence if present).
