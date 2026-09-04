PHASE:
ArubaOSCXCommandProfileCorrection

FILES:
app/vendor_profiles.py
app/collector.py
tests/test_vendor_profiles.py

ACCEPTANCE CRITERIA:
- `get_vendor_commands()` accepts an optional `platform` parameter (default `None`); when `vendor == "aruba"` and `platform` contains `"cx"` (case-insensitive), an `"aruba-cx"` profile is selected instead of the existing generic `"aruba"` profile.
- The `"aruba-cx"` profile replaces only the 5 commands the PHASE-046 field bundle recorded as rejected by the device CLI parser (`show inventory`, `show interfaces brief`, `show lldp neighbors detail`, `show switch info`, `show log buffer`) with the correct ArubaOS-CX CLI equivalents, sourced from official HPE ArubaOS-CX CLI reference documentation.
- The 5 commands the PHASE-046 field bundle recorded as accepted (`show version`, `show ip interface brief`, `show ip route`, `show arp`, `show system`) are retained unchanged in the `"aruba-cx"` profile.
- All `"aruba-cx"` commands continue to pass `validate_read_only_command()`.
- Existing `"aruba"` profile (for non-CX ArubaOS platforms, e.g. ArubaOS-Switch/ProVision) remains byte-for-byte unchanged.
- `app/collector.py` passes `identity.get("platform")` (already available via `device.metadata["identity"]`) into `get_vendor_commands()`; no other collector behaviour changes.
- Backward compatibility: any existing caller that does not pass `platform` continues to receive the current, unchanged vendor profile (including the current `"aruba"` profile) for that vendor.
- Add regression tests: `"aruba-cx"` platform selects the corrected profile, an ArubaOS platform without `"cx"` still selects the existing `"aruba"` profile, an absent/unknown platform defaults to the existing `"aruba"` profile, and all corrected commands pass `validate_read_only_command()`.
- Full suite passes.

CONSTRAINTS:
- No new dependencies.
- Do not modify SSH negotiation, timeout, retry, or recovery behaviour (app/ssh_client.py is out of scope).
- Do not modify topology discovery, traversal, or troubleshooting-scope behaviour (app/scope.py, app/topology.py, app/traversal.py are out of scope).
- Do not modify provenance or credential behaviour (app/provenance.py, app/config.py are out of scope).
- Do not implement runtime command fallback, live capability probing, or automatic retry with alternate command text in this phase; this phase corrects the static command list only.
- Do not modify cisco, juniper, or arista vendor profiles.
- If the exact ArubaOS-CX command equivalent for a rejected command cannot be confidently sourced from official documentation, retain the original command string for that entry and flag it as an open question rather than guessing.

KNOWN RISKS:
- Command syntax varies across ArubaOS-CX firmware releases; a correction verified against one documented release may not be universally correct across all deployed versions.
- No further live field device is currently available to validate the corrected profile before the next field-test opportunity.

OUTSTANDING RISKS:
- Real multi-hop topology traversal, cycle handling, and deterministic ordering against an edge-bearing topology remain unverified (carried from PHASE-046).
- DD-007 remains inconclusively validated on real hardware (unrelated, carried risk).

OPEN QUESTIONS:
- Should a future phase add runtime capability detection (probe-and-fallback) if the corrected static commands are still rejected on a subsequent field test?
- Should platform-aware command selection be generalised to other vendors (e.g. Cisco IOS vs IOS-XE) once ArubaOS-CX establishes the pattern?
