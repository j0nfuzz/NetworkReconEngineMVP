SUPERSEDED / NON-AUTHORITATIVE:
This phase was invalidly sequenced: it was executed with no dist artifact ever built from PHASE-047's changes (PHASE-047 remained uncommitted and unpackaged at execution time). Superseded by PHASE-049-ArubaOSCXFieldTestBuildPreparation. Retained for evidence/history only; do not treat as authoritative for future field-validation attempts.

---

PHASE:
ArubaOSCXCommandProfileFieldValidation

OBJECTIVE:
Validate PHASE-047's static ArubaOS-CX command profile against a reachable ArubaOS-CX device and record sanitised evidence of command acceptance or rejection.

FILES:
field_tests/
docs/FieldEvidence/PHASE-048-<timestamp>-arubaos-cx-profile-findings.md
docs/Phases/REVIEW-PHASE-048-ArubaOSCXCommandProfileFieldValidation.md
docs/Phases/IMPLEMENTED-PHASE-048-ArubaOSCXCommandProfileFieldValidation.md

ACCEPTANCE CRITERIA:
- Run the current PHASE-047 build against a reachable device detected as vendor `aruba` and platform containing `cx`.
- Confirm the collected command artifact set matches the deterministic `aruba-cx` profile order:
  `show version`, `show module`, `show interface brief`, `show ip interface brief`, `show ip route`, `show lldp neighbor-info detail`, `show arp`, `show system`, `show running-config`, `show log`.
- Classify each command as accepted, device-side parser rejected, execution failed, or not observed; do not reproduce sensitive device output outside `field_tests/`.
- Confirm whether the collection status is `collected` or `partial`, and attribute any partial status only from recorded evidence.
- Confirm the generic non-CX Aruba profile is not selected when the collected identity platform contains `cx`.
- Preserve raw field artifacts only inside `field_tests/` and write sanitised findings under `docs/FieldEvidence/`.
- Confirm provenance output is present in the produced device bundle without altering provenance implementation.
- Re-run `python -m pytest tests -q` after evidence analysis; all tests pass.

FIELD PROCEDURE:
1. Use an approved, reachable ArubaOS-CX device and a current build containing PHASE-047.
2. Run one normal collection with the existing approved device inventory and output directory under `field_tests/`.
3. Preserve the generated bundle unchanged under `field_tests/`.
4. Verify the recorded identity indicates ArubaOS-CX, then inspect command artifacts and summary data locally.
5. Produce a sanitised findings document containing only command names, outcome categories, command count, status, and provenance presence.
6. Create the required review and implemented artefacts from the sanitised evidence.

CONSTRAINTS:
- Evidence collection and documentation only; do not modify production code, dependencies, SSH handling, retry/recovery behaviour, topology discovery, provenance generation, or credential handling.
- Do not add command fallback, runtime capability detection, dynamic negotiation, or version-specific branching.
- Do not reproduce customer, site, device, hostname, IP address, serial number, software-version, user, or configuration values outside `field_tests/`.
- Do not infer command support from transport success alone; use the individual command artifact and command-failure metadata.

DECISION GATES:
- If all corrected commands are accepted, retain DD-012's static platform-aware selection and close the observed ArubaOS-CX command-profile defect for the tested platform/version.
- If one or more corrected commands are parser rejected, document the exact sanitised outcome and create a separate remediation proposal. Do not add fallback logic in this phase.
- If identity is not ArubaOS-CX or the device is unreachable, record the validation as inconclusive without changing the profile.

KNOWN RISKS:
- This validation covers only the available ArubaOS-CX platform/version and cannot establish compatibility across all firmware releases.
- `show running-config` is read-only but may collect sensitive configuration content; raw output must remain within `field_tests/`.

OUTSTANDING RISKS:
- Real multi-hop topology traversal, cycle handling, and deterministic ordering against an edge-bearing topology remain unverified from PHASE-046.
- DD-007 remains inconclusively validated on real hardware.

DDR:
- DD-012 remains Approved and governs platform-aware ArubaOS-CX profile selection.
- DD-013 is Proposed and governs evidence requirements for future static platform command-profile changes.