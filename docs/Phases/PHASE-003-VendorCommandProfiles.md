PHASE:
Vendor Command Profiles (PoC)

FILES:
- app/vendor_profiles.py
- app/collector.py
- tests/test_cli.py

ACCEPTANCE CRITERIA:
- get_vendor_commands(vendor, role=None) accepts an optional role and returns a role-specific command list when a vendor+role profile exists
- Falls back to the existing vendor-level profile when no role is given or no matching role profile exists
- Add role-specific profiles for at least cisco "switch" and cisco "router" (per Wishlist Phase 3 example)
- collector.py passes device.metadata["role"]["role"] into get_vendor_commands when present
- Existing callers that omit role continue to work unchanged (backwards compatibility)
- Tests cover: vendor+role match, vendor with unmatched role falls back, no regressions

CONSTRAINTS:
- No new SSH commands beyond documented read-only vendor/role command lists
- Maintain existing read-only command validation (validate_read_only_command)
- Do not restructure VENDOR_PROFILES beyond adding an optional role dimension
- No new dependencies
- Limit role-specific profiles to cisco switch/router only; do not add every vendor/role combination in this phase

KNOWN RISKS:
- Role-specific profile proliferation if scope is not limited
- Role misclassification (heuristic, carried from PHASE-002) could select the wrong profile depth

OUTSTANDING RISKS:
- Confidence scoring for identity/role remains unvalidated against real devices (carried from PHASE-001/002)

OPEN QUESTIONS:
- None.
