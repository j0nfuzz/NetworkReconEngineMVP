PHASE:
PHASE-084-NeighborIdentityPlatformPropagationRemediation

FILES:
- app/orchestrator.py
- tests/test_orchestrator.py

PURPOSE:
Ensure classification-derived and otherwise metadata-less devices on the sequential recursive path receive the identity probe, so DD-012 platform-aware profile selection engages for them exactly as it already does on the parallel path (PHASE-055/055A parity).

ROOT CAUSE (field-proven, FT060920262050):
- run_recursive_collection() gates _probe_identity() on device.vendor in ("auto","unknown") (PHASE-061 wiring). Neighbours enqueued from LLDP classification arrive with a concrete vendor (e.g. "aruba") and no identity metadata, so no probe runs, platform remains unknown, and get_vendor_commands() selects the vendor's base profile. On a real ArubaOS-CX neighbour this produced 6 parser rejections including the LLDP command, yielding zero discovered neighbours and blocking second-hop expansion.

ACCEPTANCE CRITERIA:
- The identity probe runs when device.vendor is in ("auto","unknown") OR device.metadata lacks a populated identity entry; devices that already carry identity metadata are not re-probed (flat-path detected devices unchanged).
- Adoption logic inside _probe_identity() is unchanged: PHASE-061A confidence gating, vendor sync, and failure-safe behaviour stay byte-identical; this phase aligns WHEN probing occurs with the approved parallel-path semantics (PHASE-055/055A), not HOW identity is adopted.
- PHASE-081/081A progress lines (probing identity / identity resolved / no confident match / identity probe failed) are emitted for every probe the new gate triggers.
- Regression test: a classification-derived neighbour (vendor "aruba", no identity metadata) whose fake probe sets vendor aruba + platform arubaos-cx reaches the collector with identity metadata populated such that the aruba-cx profile is selected (assert platform in device.metadata and command-set selection via the real get_vendor_commands()).
- Regression test: a device arriving with pre-populated identity metadata triggers no probe (fake _probe_identity raises AssertionError if invoked).
- Regression test: progress wording for the new gate path matches PHASE-081A branches.
- Full suite passes; all existing 061/061A/081/081A orchestrator tests pass unmodified.

CONSTRAINTS:
- app/orchestrator.py and its tests only; no changes to _probe_identity adoption/confidence logic, traversal, queueing, classification, checkpointing, collector, cli, parallel collector, profiles, or detector.
- No command-profile data changes: the base aruba (AOS-Switch) profile is not disproven by this evidence (its rejections occurred on CX hardware); DD-013 stands.

KNOWN RISKS:
- One additional SSH round trip per metadata-less device on the sequential path (parity with the parallel path, which already probes every device).
- Unreachable devices in recursive runs may be contacted twice (identity probe, then collection probe) before being recorded failed; bounded by max_devices and existing failure handling.
- Configured-vendor devices without identity metadata are now probed; a higher-confidence detection can adopt its vendor per the existing approved 061A/055A semantics (cross-path consistent; see OPEN QUESTIONS).

OUTSTANDING RISKS:
- SW3 second-hop discovery awaits field re-validation on a refreshed build.
- AOS-Switch profile remains field-unvalidated.
- Parallel intra-device progress lines remain deferred.

OPEN QUESTIONS:
- Whether explicit manual vendor pins should ever be overridden by higher-confidence probe adoption is a semantics question currently answered "adopt" by both paths (055A/061A precedent); raise a DDR proposal only if future field evidence shows a mis-pinned adoption.
