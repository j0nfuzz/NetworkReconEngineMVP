PHASE:
ArubaOSCXLLDPFieldValidation

OBJECTIVE:
Confirm the ArubaOS-CX platform-specific command profile (DD-012) and its governance constraints (DD-013) hold under live LLDP/neighbor discovery and recursive traversal, using the current approved portable build (dist/NetworkReconEngine.zip, commit d4ed976), not just isolated command execution (already validated in PHASE-048).

FILES:
- None (field-evidence collection only; no source or test changes anticipated).
- Evidence artefacts written under field_tests/ per FIELDTEST.md governance.

ACCEPTANCE CRITERIA:
- A full device bundle (summary.json, troubleshooting_bundle.json, build_manifest.json) is collected from a reachable ArubaOS-CX device using the approved portable build.
- topology.json correctly reflects discovered LLDP neighbors.
- Vendor/platform resolves to "aruba"/"aruba-cx" per DD-012 with expected confidence.
- Verbose CLI log captures probe/identity/vendor resolution and any probe_errors.
- No unhandled exceptions occur during recursive traversal.
- Sanitised findings are reviewed against DD-011/DD-012/DD-013.

CONSTRAINTS:
- Data-collection and review activity only; no engineering changes in this activity.
- Raw evidence must remain confined to field_tests/ per FIELDTEST.md; only sanitised findings may be written elsewhere.
- If a defect is discovered, document it but do not remediate inline; escalate as a new, separately scoped phase.
- Must use the approved PHASE-064 build artefact (commit d4ed976); do not use the earlier rejected build.

KNOWN RISKS:
- Field conditions (reachability, credentials, network access) may prevent full evidence collection on first attempt.
- Real-device LLDP output may reveal edge cases not covered by DD-012's static profile (per DD-013 governance).

OUTSTANDING RISKS:
- ArubaOSCXLLDPFieldValidation has been open since PHASE-048 pending an approved build; this activity is the first opportunity to close it.

OPEN QUESTIONS:
- None.

EVIDENCE TO COLLECT:
- Full device bundle: summary.json, troubleshooting_bundle.json, build_manifest.json.
- topology.json showing discovered LLDP neighbors.
- Verbose CLI log capturing probe/identity/vendor resolution and any probe_errors.
- Raw LLDP-related command output.

SUCCESS CRITERIA:
- Bundle collected with verifiable provenance.
- LLDP neighbors correctly appear in topology.json.
- Vendor/platform resolves to aruba/aruba-cx per DD-012 with expected confidence.
- No unhandled exceptions.

FAILURE CRITERIA:
- LLDP commands rejected by the CLI parser.
- Missing expected neighbors in the topology graph.
- Vendor/platform misdetection or confidence-gating failure on the recursive path.
- Unhandled exception during traversal.

EXIT CRITERIA:
- Sanitised findings reviewed against DD-011/DD-012/DD-013 — either confirming assumptions (workstream closes) or surfacing a defect (new scoped remediation phase defined from evidence).

RECOMMENDED MODEL FLOW:
Field execution (operator) → Claude (review sanitised findings against DDR) → if defect found, Kimi implements scoped fix → Terra reviews.
