# REVIEW-PHASE-084-NeighborIdentityPlatformPropagationRemediation

REVIEW VERDICT:
Approved

CRITICAL ISSUES:
None

MAJOR ISSUES:
None

IMPLEMENTER DEVIATION ASSESSMENT:
Accepted and endorsed. The literal phase gate ("probe every metadata-less device regardless of vendor") was correctly rejected by the Implementer: it changed configured-device behaviour beyond the field-evidenced fault class and broke this phase's own criterion that existing tests pass unmodified (observed as real TEST-NET probe attempts and a 3x suite runtime). The implemented marker-scoped gate (discovered neighbours + auto/unknown vendors) delivers the phase intent - DD-012 engagement for classification-derived neighbours - with the smallest behaviour delta. This is the deviation process working as designed: explained, minimal, recorded, reviewable.

FINDINGS REVIEWED:
- Gate extension confined to run_recursive_collection(); _probe_identity() adoption/confidence logic (PHASE-061A) byte-identical in the diff; PHASE-081/081A progress wording reused unchanged.
- Additive metadata marker at both discovered-neighbour Device construction sites (in-loop enqueue, checkpoint reconstruction); queueing filters, allowed_devices handling, classification, and checkpoint payloads unchanged - verified against the diff.
- End-to-end regression asserts the real get_vendor_commands() selects the aruba-cx profile (show module present, show trunks/show lldp neighbors detail absent) for a probed classified neighbour - directly mirroring the FT060920262050 failure.
- No-reprobe contract pinned with an AssertionError fake; devices with positive-confidence identity never re-probed.
- tests/conftest.py network-boundary fixture is consistent with the file's existing side-effect suppression pattern; probe fails fast and deterministically; connect()/run_command() surface accidental real SSH as test errors; the four PHASE-061/061A probe-logic tests still exercise the real adoption path via their own fakes.
- Reviewer independently re-ran the full suite: 346 passed, 1 pre-existing warning, runtime parity (~56s).
- Reviewer inspected the diff: production change +7/-1 in app/orchestrator.py only; tests/conftest.py +37; tests/test_orchestrator.py +90; no collector, cli, parallel collector, profile, detector, discovery, topology, classification, provenance, or SSH-transport changes.

VALIDATION ASSESSMENT:
Acceptance criteria met under the deviation-scoped semantics; validation reviewer-reproduced.

REGRESSION ASSESSMENT:
New gate path, adoption outcome, profile-selection consequence, and no-reprobe contract all pinned; all pre-existing suites pass unmodified.

CHECKPOINT ASSESSMENT:
Stable engineering checkpoint once committed with the PHASE-083 evidence artefacts.

RESIDUAL OBSERVATIONS (not blocking):
- Cross-path asymmetry persists for inventory-configured devices without identity metadata: the parallel path probes them (PHASE-055 semantics), the sequential path still does not. No field evidence requires closure; raise a DDR proposal only if future evidence demands pin-vs-probe semantics.
- Unreachable discovered neighbours incur two connection attempts (identity probe, collection probe) before failure recording - documented known risk; bounded by max_devices.
- Console line-ordering observation from PHASE-083 (Starting/Finished lines emitted after the command stream) remains an observability polish candidate.

CLOSURE RECOMMENDATION:
On commit: close PHASE-083 (by evidence) and PHASE-084 (approved).

DDR REVIEW:
UNCHANGED DD:DD-008

OUTSTANDING RISKS:
- SW3 second-hop discovery unproven until field re-validation on a refreshed build.
- AOS-Switch profile remains field-unvalidated (DD-013).
- Parallel intra-device progress deferred.

OPEN QUESTIONS:
None

RECOMMENDED NEXT PHASE:
PHASE-085-FieldValidationBuildRefresh-084Checkpoint

STABLE CHECKPOINT:
STABLE CHECKPOINT

COMMIT MESSAGE:
PHASE-083/084: field validation closure and neighbor identity platform propagation

PUSH DECISION:
PUSH RECOMMENDED

COMMANDS:
git add app/orchestrator.py tests/conftest.py tests/test_orchestrator.py docs/PROJECT-JOURNAL.md docs/FieldEvidence/PHASE-083-20260906-2050-fieldvalidation-findings.md docs/Phases/PHASE-083-FieldValidationPost081A.md docs/Phases/PHASE-084-NeighborIdentityPlatformPropagationRemediation.md docs/Phases/IMPLEMENTED-PHASE-084-NeighborIdentityPlatformPropagationRemediation.md docs/Phases/REVIEW-PHASE-084-NeighborIdentityPlatformPropagationRemediation.md
git commit -m "PHASE-083/084: field validation closure and neighbor identity platform propagation"
git push
