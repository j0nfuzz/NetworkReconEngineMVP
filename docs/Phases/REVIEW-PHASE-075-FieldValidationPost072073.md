# REVIEW-PHASE-075-FieldValidationPost072073

REVIEW VERDICT:

Not Approved

CRITICAL ISSUES:

None

MAJOR ISSUES:

Issue:
Recursive collection buffers every result, then emits verbose device messages and writes device bundles only after `run_recursive_collection()` returns.

Why It Matters:
Long runs provide no live output or per-device artefacts, preventing operational monitoring and recovery evidence during collection.

Recommended Fix:
Add a per-device completion callback that writes the bundle and emits progress as each collection completes.

Issue:
The portable field bundle records `build_provenance.json` `head_commit_sha: unknown`.

Why It Matters:
PHASE-075 cannot prove it used the approved PHASE-074 build, violating its provenance acceptance criterion and DD-008 evidence traceability.

Recommended Fix:
Embed build provenance into the portable runtime and use it when Git metadata is unavailable.

DDR REVIEW:

UNCHANGED DD:DD-008

OUTSTANDING RISKS:

- Ubiquiti UAP and Netgear GS748Tv5 neighbors are discovered with IPs but classify as unknown and remain intentionally unqueued.
- HOSTNAME-06 failed authentication; its neighbors cannot be discovered until credentials/access are corrected.

OPEN QUESTIONS:

None