PHASE:
PHASE-086-FieldValidationPost084-SecondHopTraversal

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
