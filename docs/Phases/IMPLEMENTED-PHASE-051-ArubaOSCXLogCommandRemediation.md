# IMPLEMENTED-PHASE-051-ArubaOSCXLogCommandRemediation

## Phase
PHASE-051-ArubaOSCXLogCommandRemediation

## Status
Implemented

## Objective
Correct the single ambiguous ArubaOS-CX command left after PHASE-047's field validation, replacing `show log` with its documented, unambiguous equivalent while preserving all other field-validated commands.

## Files Changed
- `app/vendor_profiles.py`
  - Replaced `"show log"` with `"show logging"` in the `"aruba-cx"` profile.
  - The other nine `"aruba-cx"` commands remain byte-for-byte unchanged.
- `tests/test_vendor_profiles.py`
  - Updated `ARUBA_CX_PROFILE_COMMANDS` fixture to expect `"show logging"`.
  - Updated `test_aruba_cx_profile_replaces_rejected_commands` assertion.
  - Added `test_aruba_cx_profile_replaces_ambiguous_log_command` to explicitly assert that `"show log"` is absent and `"show logging"` is present.

## Source Justification
The replacement command is `show logging`.

Justification:
- Official HPE ArubaOS-CX CLI references use `show logging` to display system event logs.
- The command is a read-only `show` command and unambiguously resolves the `% Ambiguous command` failure returned by the shorter `show log` form on the evidenced platform/version.
- It is functionally analogous to logging display commands on other vendor profiles already used in the codebase (e.g., Cisco `show logging`, Arista `show logging`).
- The command passes the existing `validate_read_only_command()` policy gate (`show` prefix, no blocklisted verb).

## Validation Results
- `python -m pytest tests/test_vendor_profiles.py tests/test_cli.py -q`: 100 passed
- `python -m pytest tests -q`: 230 passed
- `git diff --check`: clean

## Constraints Respected
- No SSH, topology, traversal, recursion, credential, or provenance code changed.
- No new dependencies added.
- No command coverage expansion beyond the single evidenced log command.
- No runtime fallback or probing logic added.
- The generic `"aruba"` (non-CX) profile and all other vendor profiles remain unchanged.
- Deterministic command ordering preserved (list is treated as an ordered sequence and the replacement preserves position).

## Risks
- ArubaOS-CX logging command syntax can still vary by firmware release; `show logging` is sourced from official documentation but remains to be revalidated against the same platform/version on the next field run.

## Next Recommended Action
- Re-run field validation against the same or an equivalent reachable ArubaOS-CX device using a build containing this PHASE-051 change, specifically confirming that `show logging` returns valid output and that the profile now achieves 10/10 command acceptance on the target platform/version.
