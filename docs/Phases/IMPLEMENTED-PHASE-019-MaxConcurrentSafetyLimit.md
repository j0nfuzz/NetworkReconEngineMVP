PHASE:
MaxConcurrentSafetyLimit

STATUS:
Implemented

FILES MODIFIED:
- app/parallel_collector.py
- app/cli.py
- tests/test_parallel_collector.py
- docs/PROJECT-JOURNAL.md

TESTS ADDED:
- tests/test_parallel_collector.py::test_max_concurrent_above_ceiling_is_clamped (parametrized for 11, 50, 100)
- tests/test_parallel_collector.py::test_max_concurrent_within_range_unchanged
- tests/test_parallel_collector.py::test_cli_help_text_documents_ceiling

DDR UPDATES:
UNCHANGED DD:DD-005

RISKS INTRODUCED:
- Hard ceiling of 10 may be too low for some fault domains; override requires a future config phase.

RISKS RESOLVED:
- --max-concurrent no longer allows unbounded simultaneous SSH sessions, reducing AAA/RADIUS/TACACS overload risk.

OPEN ISSUES:
- Should the ceiling be configurable via device inventory/global config in a later phase?
