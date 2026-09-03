PHASE:
FieldEvidencePostDiagnosticRefresh

STATUS:
Implemented

FILES MODIFIED:
- docs/Phases/PHASE-040-FieldEvidencePostDiagnosticRefresh.md
  - Created the architect phase definition artefact (pre-existing).
- docs/FieldEvidence/PHASE-040-20260903-183540-bundle-findings.md
  - Recorded fresh field evidence collection attempt against the current approved commit.
  - Documented build provenance (HEAD SHA, dirty patch, SHA-256 checksum) for the bundle.
- docs/PROJECT-JOURNAL.md
  - Appended delta entry for PHASE-040 evidence collection.

TESTS ADDED:
- None (this phase is evidence capture and documentation only).

DDR UPDATES:
UNCHANGED DD:DD-007

RISKS INTRODUCED:
- None.

RISKS RESOLVED:
- The PHASE-037-carried "fresh field evidence" risk has been actioned by executing a live collection run.
- Provenance instrumentation (DD-008) was exercised on a live run and produced complete build_provenance.json artefacts even when no device was reachable.

OPEN ISSUES:
- The configured sample devices (192.168.2.1, 192.168.2.2, 192.168.2.3) were unreachable, so no timeout/recovery events were captured.
- DD-007 behaviour on real hardware remains inconclusively validated.
- An interactive device configuration exists in `config/interactive_devices.yml`; using it requires explicit authorization.
