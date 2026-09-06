PHASE:
PHASE-084-NeighborIdentityPlatformPropagationRemediation

STATUS:
Implemented

ROOT CAUSE (field-proven, FT060920262050):
- run_recursive_collection() gated _probe_identity() on vendor auto/unknown only (PHASE-061). Classification-derived neighbours (vendor "aruba" from PHASE-072 LLDP markers, no identity metadata) skipped the probe, so platform stayed unknown and DD-012 could not select the aruba-cx profile on a real ArubaOS-CX neighbour: 6/13 parser rejections including the LLDP command, zero discovered neighbours, downstream device never discovered.

FILES MODIFIED:
- app/orchestrator.py:
  * Identity-probe gate extended: probe runs when vendor is auto/unknown OR the device is a discovered neighbour (metadata marker) lacking positive-confidence identity metadata. Adoption logic inside _probe_identity() untouched (PHASE-061A semantics byte-identical); PHASE-081/081A progress lines reused unchanged.
  * Discovered-neighbour Device constructions (in-loop enqueue and checkpoint reconstruction) now carry metadata={"discovered_neighbor": True}; queueing, filtering, and traversal logic unchanged.
- tests/test_orchestrator.py: 3 regressions - classified neighbour probe -> platform populated -> real get_vendor_commands selects aruba-cx (11 commands, no AOS-S verbs); pre-populated identity metadata -> _probe_identity raises if invoked (no re-probe); progress lines emitted for the new gate path.
- tests/conftest.py: autouse network-boundary fixture stubbing app.orchestrator.DeviceSSHClient for tests that do not provide their own fake, because the extended gate makes previously probe-free orchestrator tests reach the real probe path against TEST-NET addresses. Tests exercising probe logic patch their own fakes and override the fixture.

IMPLEMENTER DEVIATION (recorded for reviewer):
- The phase definition proposed gating on "metadata lacks identity, regardless of vendor". Implementing that literally caused existing tests to attempt real SSH probes and would have added identity probing (and potential vendor adoption per 061A) for inventory-configured devices - beyond the evidenced fault class and contrary to this phase's own criterion that existing tests pass unmodified. The implemented gate scopes the extension to classification-derived discovered neighbours (the exact field-evidenced class) via an additive metadata marker, achieving cross-path parity where it matters (the parallel path probes every device; the sequential path now probes every discovered neighbour). Configured-device probing semantics remain exactly as before.

VALIDATION:
- Full suite: 346 passed, 1 pre-existing warning (56.6s; runtime parity with the pre-change suite after the conftest boundary fixture).
- Interim observed and resolved: suite hang/161s runtime from real TEST-NET probes (diagnosed, fixed via the conftest fixture).

DIFF SUMMARY:
- app/orchestrator.py +7/-2; tests/test_orchestrator.py +63; tests/conftest.py +40.

REGRESSION COVERAGE:
- New neighbour platform-propagation path pinned end-to-end through the real profile selector.
- No-reprobe contract pinned (AssertionError fake).
- All existing 061/061A/081/081A orchestrator tests pass unmodified; the four _probe_identity logic tests continue to exercise the real adoption path with their own fakes.

SCOPE CONFIRMATION:
- No changes to _probe_identity adoption/confidence logic, traversal, queueing filters, classification, checkpointing, collector, cli, parallel collector, vendor profiles, or detector. No profile data changes (AOS-S profile not disproven by this evidence; DD-013 stands).

DDR UPDATES:
UNCHANGED DD:DD-008

RISKS INTRODUCED:
- One additional identity-probe SSH round trip per discovered neighbour on the sequential path (parity with the parallel path).
- Unreachable neighbours are contacted twice (identity probe, then collection probe) before being recorded failed; bounded by existing failure handling and max_devices.

RISKS RESOLVED:
- DD-012 platform-aware profile selection now engages for classification-derived neighbours on the default recursive journey; the FT060920262050 CX-neighbour wrong-profile defect and its downstream expansion consequence are closed pending field re-validation.

OPEN ISSUES:
- SW3 second-hop discovery awaits field re-validation on the refreshed build.
- Manual-vendor-pin vs probe-adoption semantics remain an open DDR question (unchanged by this phase).
