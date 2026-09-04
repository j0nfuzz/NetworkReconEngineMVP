PHASE:
ArubaOSCXLogCommandRemediation

FILES:
app/vendor_profiles.py
tests/test_vendor_profiles.py

ACCEPTANCE CRITERIA:
- The `"aruba-cx"` profile's `show log` entry is replaced with the correct read-only ArubaOS-CX CLI equivalent, sourced from official HPE ArubaOS-CX CLI reference documentation for the platform/version evidenced in PHASE-050 sanitised findings.
- The other nine `"aruba-cx"` commands (already field-validated as accepted in PHASE-050) remain byte-for-byte unchanged.
- The replacement command continues to pass `validate_read_only_command()`.
- If the exact ArubaOS-CX equivalent cannot be confidently sourced from official documentation, retain the current `show log` string and record this as an open question rather than guessing (same rule as PHASE-047).
- Add/extend a regression test in `tests/test_vendor_profiles.py` asserting the corrected log command is present in the `"aruba-cx"` profile and passes the read-only policy check.
- Full regression suite passes (`python -m pytest tests -q`).
- Existing `"aruba"` (non-CX) profile remains unchanged.

CONSTRAINTS:
- No new dependencies.
- Do not modify SSH negotiation, timeout, retry, or recovery behaviour (app/ssh_client.py out of scope).
- Do not modify topology discovery, traversal, or troubleshooting-scope behaviour (app/scope.py, app/topology.py, app/traversal.py, app/orchestrator.py, app/parallel_collector.py out of scope).
- Do not modify provenance or credential behaviour.
- Do not implement runtime command fallback, live capability probing, or command-coverage expansion in this phase; this phase corrects the single evidenced `show log` defect only.
- Do not modify cisco, juniper, or arista vendor profiles.
- Do not reproduce any field_tests/ hostnames, IPs, or other sensitive identifiers in source, tests, or documentation; use sanitised references only (per FIELDTEST.md).

KNOWN RISKS:
- ArubaOS-CX log command syntax may vary by firmware release; a correction verified against one documented release may not be universally correct.
- No live ArubaOS-CX device is guaranteed available before the next field-test opportunity to revalidate.

OUTSTANDING RISKS:
- Running-config output completeness remains unverified (carried from PHASE-050; tracked separately as RunningConfigCaptureCompletenessValidation, not in scope here).
- Real multi-hop topology traversal remains architecturally limited to a configured seed device (carried from PHASE-046/050; tracked separately as AutomaticTraversalRootSelection/DefaultRecursiveDiscoveryBehaviour, not in scope here).
- DD-007 remains inconclusively validated on real hardware (unrelated, carried risk).

OPEN QUESTIONS:
- What is the exact, documented, read-only ArubaOS-CX CLI command that returns log buffer contents on the evidenced platform/version (candidates require verification against official HPE documentation before being written into the profile)?
- Once this phase closes, should PHASE-050 field validation be re-executed to confirm 10/10 command acceptance, or is a smaller re-test of `show log` alone sufficient evidence?
