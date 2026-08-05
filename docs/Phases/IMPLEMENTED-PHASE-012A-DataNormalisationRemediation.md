PHASE:
PHASE-012A-DataNormalisationRemediation

STATUS:
Implemented

FILES MODIFIED:
- app/normalization.py
  - `_find_cisco_interface_errors()` now evaluates every supported counter (`input errors`, `output errors`, `CRC`) on an interface detail line using `re.finditer()`.
  - An interface is flagged when any parsed counter is nonzero.
  - Existing summary shape, field names, safe defaults, and raw-bundle immutability are preserved.
- tests/test_normalization.py
  - Imported `_find_cisco_interface_errors` for targeted regression coverage.
  - Added regression tests for the exact false-negative case and a mixed-counters case.

TESTS ADDED:
- tests/test_normalization.py::test_find_cisco_interface_errors_detects_nonzero_crc_after_zero_input_errors
- tests/test_normalization.py::test_find_cisco_interface_errors_evaluates_multiple_counters

DDR UPDATES:
UNCHANGED DD:2026-08-04

RISKS INTRODUCED:
- None.

RISKS RESOLVED:
- False-negative interface error detection when the first counter is zero but a later counter on the same line is nonzero.

OPEN ISSUES:
- None.
