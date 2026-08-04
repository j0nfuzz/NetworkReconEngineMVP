PHASE:
Vendor Command Profiles (PoC)

STATUS:
Implemented

FILES MODIFIED:
- app/vendor_profiles.py
- app/collector.py
- tests/test_cli.py

TESTS ADDED:
- tests/test_cli.py::test_vendor_commands_role_specific_cisco_switch
- tests/test_cli.py::test_vendor_commands_role_specific_cisco_router
- tests/test_cli.py::test_vendor_commands_unmatched_role_falls_back

DDR UPDATES:
- DD-003 status updated to Approved (implementation matches proposed role-dimension extension).

RISKS INTRODUCED:
- Cisco role profiles are heuristic-driven; role misclassification selects an inappropriate command set.
- Role-specific profiles may diverge from vendor-level profiles over time if not kept in sync.

RISKS RESOLVED:
- Vendor and role metadata now translate into role-appropriate collection depth.

OPEN ISSUES:
- Role profiles exist only for cisco switch/router; other vendor/role combinations remain vendor-level.
