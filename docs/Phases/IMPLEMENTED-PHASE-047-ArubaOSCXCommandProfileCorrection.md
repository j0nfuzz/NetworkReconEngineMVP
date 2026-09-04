PHASE:
ArubaOSCXCommandProfileCorrection

STATUS:
Implemented

FILES CHANGED:
- app/vendor_profiles.py
  - Added `"aruba-cx"` command profile.
  - Extended `get_vendor_commands(vendor, role=None, platform=None)` with platform-aware selection: when `vendor == "aruba"` and `platform` contains `"cx"` (case-insensitive), the `"aruba-cx"` profile is used.
  - Existing `"aruba"`, `"cisco"`, `"juniper"`, `"arista"`, and `"generic"` profiles are unchanged.
- app/collector.py
  - Extracts `platform` from `device.metadata["identity"]` and passes it to `get_vendor_commands()`.
  - No changes to SSH, retry, recovery, topology, provenance, or credential handling.
- tests/test_vendor_profiles.py (new file)
  - Regression tests for platform-aware profile selection, read-only policy compliance, deterministic ordering, role fallback, and backward compatibility.
- tests/test_cli.py
  - Updated three `app.collector.get_vendor_commands` monkeypatch lambdas to accept the new optional `platform` argument.

FILES ANALYSED BUT NOT CHANGED:
- app/ssh_client.py (out of scope)
- app/provenance.py (out of scope)
- app/config.py (out of scope)
- app/scope.py / app/topology.py / app/traversal.py (out of scope)
- app/parallel_collector.py (left unchanged; `get_vendor_commands` remains backward-compatible for callers that do not supply `platform`)

COMMAND PROFILE CHANGES:
The `"aruba-cx"` profile retains the 5 commands that succeeded on the observed ArubaOS-CX device:
- show version
- show ip interface brief
- show ip route
- show arp
- show system

It replaces the 5 commands that were rejected by the device CLI parser:
| Generic Aruba Profile (rejected) | ArubaOS-CX equivalent |
|----------------------------------|-----------------------|
| show inventory                   | show module           |
| show interfaces brief            | show interface brief  |
| show lldp neighbors detail       | show lldp neighbor-info detail |
| show switch info                 | show running-config   |
| show log buffer                  | show log              |

All replacement commands pass `validate_read_only_command()`.

VALIDATION RESULTS:
- `python -m pytest tests/test_vendor_profiles.py tests/test_cli.py -q`
  - 99 passed
- `python -m pytest tests -q`
  - 229 passed

Note: running `python -m pytest -q` from the workspace root collides with the archived `audit/tests` copy due to an import-name clash; this is a pre-existing environment/layout issue, not a regression caused by this phase. The active `tests` directory suite passes in full.

DDR UPDATES:
- DD-012 status updated from `Proposed / Pending GPT Reviewer approval` to `Approved` (Approver: GPT Reviewer, Date: 2026-09-04).

DEVIATIONS FROM SCOPE:
- Updated three monkeypatch lambdas in `tests/test_cli.py` so existing tests remain compatible with the new optional `platform` parameter. This is a test-only, signature-compatibility change and does not alter production behaviour.
- `app/parallel_collector.py` was not modified because the phase scope explicitly targeted `app/collector.py`. The parallel collector continues to work via the backward-compatible default (`platform=None`), selecting the unchanged generic `aruba` profile.

RISKS INTRODUCED:
- ArubaOS-CX CLI syntax can vary by firmware release; the corrected commands are sourced from official HPE ArubaOS-CX CLI reference documentation but cannot be live-validated in this environment until the next field-test opportunity.
- The `show running-config` replacement for `show switch info` exposes configuration data; it is read-only and begins with `show`, so it passes the existing read-only policy gate.

RISKS RESOLVED:
- Removes the confirmed command-profile mismatch for ArubaOS-CX without touching vendor detection, SSH negotiation, retry/recovery, topology discovery, provenance generation, or credential handling.

OPEN ISSUES:
- No live ArubaOS-CX device is currently reachable to revalidate the corrected profile.
- Generalising platform-aware profiles to other vendors (e.g. Cisco IOS vs IOS-XE) is deferred to a future phase.
