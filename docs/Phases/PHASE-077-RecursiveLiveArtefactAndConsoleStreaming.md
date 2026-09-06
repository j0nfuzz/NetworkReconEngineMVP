PHASE:
PHASE-077-RecursiveLiveArtefactAndConsoleStreaming

FILES:
- app/cli.py
- app/orchestrator.py

ACCEPTANCE CRITERIA:
- Each device bundle is written to disk immediately after that device's collection completes, not after the entire recursive traversal returns.
- "[verbose] Starting device" / "[verbose] Finished collection" lines print immediately per device, not batched at the end.
- bundle_manifest.json and topology.json are updated incrementally (or written per-device) so an interrupted run leaves usable partial artefacts.
- Regression test proves per-device bundle files exist on disk before traversal completes (e.g. via a collection callback/hook assertion).
- No change to collection order, classification, or queueing logic (already validated in PHASE-075 field evidence).

CONSTRAINTS:
- No changes to timeout, SSH, recovery, traversal, or classification behavior.
- No changes to checkpoint schema beyond what is needed to stream artefacts.
- Reuse the existing on_collected callback path in app/orchestrator.py rather than introducing new concurrency.

KNOWN RISKS:
- Streaming writes increase I/O calls per device; acceptable for expected device-count scale.

OUTSTANDING RISKS:
- build_provenance.json head_commit_sha:unknown in portable field bundles remains open (PHASE-076, deferred; traceable via build_manifest.json in the interim).

OPEN QUESTIONS:
- None.
