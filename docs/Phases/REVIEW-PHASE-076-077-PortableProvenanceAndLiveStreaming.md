# REVIEW-PHASE-076-077-PortableProvenanceAndLiveStreaming

REVIEW VERDICT:

Not Approved

CRITICAL ISSUES:

None

MAJOR ISSUES:

Issue:
`RUNTIME_PROVENANCE_PATH` resolves to `python/build_runtime_provenance.json`, while `build_portable.py` writes `build_runtime_provenance.json` to the bundle root.

Why It Matters:
Portable runtime provenance fallback cannot find the embedded file, so field bundles still record an unknown commit when no Git repository exists.

Recommended Fix:
Resolve the runtime provenance file relative to the bundle root or write it beside the embedded interpreter; add an extracted-bundle integration test.

Issue:
`--target-device` invokes `run_parallel_scoped_collection`, which receives no per-device streaming callback and retains end-of-run bundle/log writes.

Why It Matters:
Recursive scoped collection does not meet PHASE-077 live-artifact/console requirements.

Recommended Fix:
Extend the existing parallel collection callback contract to stream completed device bundles through the same CLI handler.

Issue:
`console.log` records only messages sent through `_VerboseTee`; the final generated-manifest console message is printed directly and is not captured.

Why It Matters:
The stated automatic console capture is incomplete.

Recommended Fix:
Route final CLI status output through the console-capture writer.

DDR REVIEW:

UNCHANGED DD:DD-008

OUTSTANDING RISKS:

- Portable provenance remains unverified and non-functional with the current path mismatch.
- Scoped recursive runs retain deferred output behavior.

OPEN QUESTIONS:

None