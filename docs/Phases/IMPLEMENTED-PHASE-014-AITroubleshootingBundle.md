PHASE:
PHASE-014-AITroubleshootingBundle

STATUS:
Implemented

FILES MODIFIED:
- app/troubleshooting.py (new)
  - Added `build_troubleshooting_bundle(summary, health, raw_outputs)`.
  - Returns a deterministic AI-ready briefing including device identity, health score, warnings, critical findings, sorted evidence source names, and a plain-text brief.
  - References raw evidence by command/source name only; does not copy command output into the brief.
  - Safe defaults for missing or empty inputs; inputs are not mutated.
- tests/test_troubleshooting.py (new)
  - Added regression tests for complete bundle generation, missing-data handling, deterministic shape/order, evidence referencing, and input immutability.

TESTS ADDED:
- tests/test_troubleshooting.py::test_build_troubleshooting_bundle_complete
- tests/test_troubleshooting.py::test_build_troubleshooting_bundle_missing_data
- tests/test_troubleshooting.py::test_build_troubleshooting_bundle_deterministic_shape
- tests/test_troubleshooting.py::test_build_troubleshooting_bundle_evidence_is_referenced
- tests/test_troubleshooting.py::test_build_troubleshooting_bundle_does_not_mutate_inputs

DDR UPDATES:
UNCHANGED DD:2026-08-04

RISKS INTRODUCED:
- Briefing is generic until future vendor- and topology-aware analysis phases.

RISKS RESOLVED:
- None.

OPEN ISSUES:
- None.
