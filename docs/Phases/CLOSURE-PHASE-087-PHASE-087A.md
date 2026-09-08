# CLOSURE-PHASE-087-PHASE-087A

Assessment date: 2026-09-08. Architectural governance follow-up; no implementation or new code review.

## Decisions

- PHASE-087 and PHASE-087A remain **closed together**. The original PHASE-087 rejection remains part of the historical record; PHASE-087A resolves its identified acceptance failure.
- **MVP achieved** for the defined seed-to-supported-neighbour-to-troubleshooting-package workflow. This does not mean complete physical inventory, all-vendor support, or completion of the entire Wishlist.
- **DD-016 remains Approved**, as already recorded in the canonical DDR. Terra's PHASE-087A review explicitly supports combined closure and governance re-approval; no new approval is being invented here.
- **Additional product remediation required: No**, on the evidence reviewed. Documentation qualifications and a narrower next-phase definition are justified.

## Evidence and limits

Sources read: the governing prompt and standard; the latest five journal entries; the entire DDR; Wishlist Phase 4; the definitions, implementation reports and reviews for PHASE-087/087A; the PHASE-086 findings; and relevant contents of FT070920261340.zip. Existing closure and PHASE-088 definitions were also assessed. Field-derived descriptions below are sanitised under field_tests/FIELDTEST.MD.

| Evidence | What it establishes | Limit |
|---|---|---|
| ZIP SHA-256 4BD6ADFB7CDAB70549473B8FA1A563E5A56465928766E876B684AE1D9DD4972E; all three provenance records identify clean build 462bf4366d0121b17209856059df9258bc428309 | Correct PHASE-085 field bundle, predating PHASE-087/087A | Cannot prove a post-fix live run |
| Device summaries, raw command evidence and console | Two distinct physical switches collected successfully; 11 commands and zero recorded failures per collection; one redundant seed-alias collection | Three collection records do not mean three distinct collected switches |
| Downstream raw LLDP versus summary | 4 raw entries and 4 parsed records; one AP, two unidentified advertisements, and the seed back-link | Unknown advertisements do not establish device type; counts alone are not a physical inventory |
| Seed raw LLDP versus summary | 10 raw entries and 10 parsed records, including a further switch-class neighbour also retained in topology | That neighbour was not collected; the user confirmed on 2026-09-08 that it is a different device from SW3 |
| Summary, troubleshooting bundle, prompt, topology, manifest, console and provenance members | Usable evidence package and recorded collection progress | A static ZIP alone does not establish timing of every live update |
| PHASE-087 implementation/review | Sequential and parallel dedup regressions; 54 focused and 350 full-suite tests reported; topology gap correctly rejected | Collection tests are not fresh live post-fix evidence |
| Terra PHASE-087A review | Canonical alias back-edge reproduction; preserved alias/address; 11 focused and 354 full-suite tests reported; combined closure recommended | Resolves the matched-alias case, not a guarantee that every uncollected neighbour has a collected node |

The field run demonstrates the MVP collection workflow. Reviewed regression tests and the topology reproduction establish the two subsequent fixes. No post-PHASE-087A field archive was supplied for this assessment. That distinction qualifies the validation claim without reopening the approved fixes or making another field run a closure gate.

## SW3 assessment

- **Proven defect:** none established by SW3's absence. The earlier duplicate-identity and alias-target defects are closed.
- **Expected current behaviour:** LLDP/CDP-driven traversal cannot enqueue a device for which it has no usable advertised neighbour identity. The downstream LLDP capture contains no identified SW3 record and has no observed parser loss.
- **Unresolved environmental fact:** why SW3 is absent from that capture. Neither LLDP being disabled nor an absent physical link has been proven. Physical rack presence does not establish attachment to the collected downstream switch.
- **Future capability opportunity:** additional evidence could expose reachability or topology candidates, but cannot be promised to discover SW3.
- The user's confirmation excludes the additional seed-advertised switch as SW3. No supplied SW3 management/chassis/interface identity allows anonymous advertisements or other table entries to be matched conclusively. The earlier claim that SW3 has no evidence anywhere must therefore be read as "no positively identified SW3 evidence", not proof of nonexistence or of a particular cause.

## Architecture assessment

Current neighbour extraction is **LLDP/CDP**, not strictly LLDP-only: app/discovery.py::extract_neighbors dispatches only those command outputs, and app/collector.py places those records into discovered_neighbors. Preserve that proven path.

It is not a permanent LLDP/CDP-only product commitment. Wishlist Phase 4 explicitly includes ARP, routing and vendor topology information. It does not explicitly list MAC tables in that phase, contrary to the previous journal wording. The existing Aruba-CX profile and archive already include MAC, ARP, routes and interface outputs; another MAC collection command is unnecessary for the observed platform.

LLDP advertises information to directly connected devices. Its absence alone cannot explain a missing rack device. See [Cisco LLDP documentation](https://www.cisco.com/c/en/us/td/docs/switches/lan/c9000/lyr2-fwd/cdp-lldp-mac-udld/cdp-lldp-mac-udld-configuration-guide/c-configure-lldp.html).

MAC learning associates a frame's source address with an ingress port and VLAN; entries age, and an OUI identifies a manufacturer. Our architectural inference is that even a unique learned port or matching OUI cannot alone prove immediate switch adjacency or a particular chassis identity. See [Cisco MAC learning documentation](https://www.cisco.com/c/en/us/td/docs/switches/lan/c9000/lyr2-fwd/cdp-lldp-mac-udld/cdp-lldp-mac-udld-configuration-guide/c-configure-mac.html). [HPE's MAC table reference](https://arubanetworking.hpe.com/techdocs/AOS-CX/10.17/HTML/l2_bridging_4100i-6000-6100-5420-6200/Content/Chp_mac/mac_cmds/sho-mac-add-tab-vla.htm) also distinguishes VLAN and learned/configured entries; it is semantic context, not field validation of another release.

## Next activity and classification

Exactly **one selected next activity**, within the maximum of five concurrent workstreams:

| Recommendation | Classification | Disposition |
|---|---|---|
| PHASE-089-SW3DiscoveryEvidenceAssessment | Enhancement: evidence qualification prerequisite | Sole selected next phase; defined, not executed |
| PHASE-088-MacAddressTableTopologyEnrichment | Future roadmap | Existing proposal revised and deferred until PHASE-089 and DDR review justify activation |
| ARP correlation and interface correlation | Future roadmap | Reuse existing evidence during PHASE-089; no new production feature phase now |
| LACP membership and STP topology | Future roadmap | Potential corroboration of aggregation and forwarding relationships; no phase activation |
| Routing-neighbour correlation | Future roadmap | Logical Layer-3 relationships must remain distinct from physical links; captured routes alone are not neighbour-session evidence |
| OUI/vendor hints | Future roadmap | Supporting annotation only; cannot identify SW3 or establish an edge independently |

No required-remediation phase is created. Do not fill spare workflow capacity merely to keep work moving.

PHASE-089's purpose, boundary and implementer handover are defined only in its phase file. It can conclude "unresolved" with precise missing evidence; it must not manufacture a defect or make SW3 discovery its pass condition.

## DDR and journal disposition

- DD-016: unchanged Approved; existing approval evidence is sufficient.
- DD-017: revised **Proposed**. Remove the unsupported explanation of SW3's absence and permanent architecture freeze. Preserve LLDP/CDP behaviour while requiring source and uncertainty separation for any future enrichment. Reviewer approval remains pending.
- PROJECT-JOURNAL.md: append a dated correction/decision delta; preserve all earlier entries. The new entry qualifies earlier field-validation and Wishlist claims rather than rewriting history.

## Final recommendation

Keep PHASE-087/087A closed and DD-016 Approved. Accept the scoped MVP. Execute PHASE-089 next to establish SW3 identity and visibility using existing evidence, supplemented only by a bounded field capture if needed. Decide any production enhancement from that result; do not implement the former MAC/OUI-to-edge proposal now.
