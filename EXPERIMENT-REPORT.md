# Experiment report — PHASE-090

Date: 8 September 2026. Outcome: completed engineering experiment with a working prototype. This report assesses the documented workflow and available evidence; it does not measure comparative model quality, speed or cost.

## Objective and scope

Explore whether a human-directed Architect → Implementer → Reviewer process using AI agents could incrementally build and validate a network reconnaissance tool while keeping decisions, acceptance criteria and corrections traceable.

The practical target was a seed-to-supported-neighbour-to-troubleshooting-package workflow: collect diagnostic SSH output, identify the platform, extract neighbours, traverse eligible devices, retain raw evidence and produce structured artefacts. Production certification, exhaustive physical inventory and completion of every Wishlist item were outside the demonstrated outcome.

The runtime is deterministic software. AI was used in engineering and can consume the resulting troubleshooting prompts; it is not a prerequisite for collection.

## Method and roles

| Participant | Responsibility and observed contribution |
|---|---|
| Architect | Selected bounded phases, defined acceptance and constraints, assessed new evidence and recorded design decisions |
| Implementer | Changed the scoped files, wrote regressions and documented implementation results |
| Reviewer | Compared implementation with acceptance criteria, inspected outputs, ran checks and approved or rejected |
| Human operator/project owner | Chose goals, provided credentials/access, operated field builds, supplied archives and network context, corrected mistaken assumptions and authorised phase transitions |

The project standard originally names Claude, Kimi and GPT respectively; phase records also identify Terra as reviewer. This report describes role separation evidenced in the records. It does not establish independent model execution, equivalent prompts, equal budgets or a controlled human-versus-AI trial.

The journal is append-only; the decision register records current disposition; phase definitions, implementation reports and reviews explain each change. Historical statements are retained even when later evidence qualifies them. The current closure documents give the resulting interpretation.

## Evidence and major findings

| Evidence | Finding | Boundary |
|---|---|---|
| PHASE-086 field findings and direct archive inspection | Three successful collection records, 11 commands each, zero recorded failures; two distinct physical switches because one record revisited the seed under an alias | The clean build was `462bf4366d0121b17209856059df9258bc428309`, before PHASE-087/087A |
| Downstream raw LLDP and parsed summary | Four raw records and four parsed neighbours; the platform-aware Aruba-CX profile succeeds | No positively identified additional rack switch; neither nonexistence nor attachment is proven |
| Console, manifest, raw files, summaries, prompts, topology and provenance | Usable end-to-end troubleshooting evidence was produced | A static archive cannot prove every live write's timing |
| PHASE-087 review | Collection deduplication passed its regressions, but the required canonical topology back-edge was missing | A green 350-test suite did not establish every acceptance criterion |
| PHASE-087A review | Direct before/after reproduction and 11 topology tests established canonical alias resolution; 354 full-suite tests passed | Reviewed regression/reproduction evidence, not a new post-fix live archive |
| PHASE-090 verification | Current working tree again passes 354 tests with one established warning | At initial assessment the source edits were uncommitted; the subsequent user-authorised closure commit captures that same reviewed implementation |

Primary sources: [PHASE-086 findings](docs/FieldEvidence/PHASE-086-20260907-1340-secondhop-findings.md), [PHASE-087 review](docs/Phases/REVIEW-PHASE-087-DeviceIdentityDeduplicationByHostname.md), [PHASE-087A review](docs/Phases/REVIEW-PHASE-087A-TopologyAliasBackEdgeRemediation.md), and [qualified combined closure](docs/Phases/CLOSURE-PHASE-087-PHASE-087A.md). These historical sources are retained for restricted review and contain identifiers; the examples here are synthetic.

## Worked example: rejection followed by approval

Use the synthetic identities `192.0.2.10` (seed), `SWITCH-02` (downstream) and `SWITCH-01` (the seed's advertised name).

1. The downstream switch advertises `SWITCH-01` at the seed's management address. Name-only visited sets treat it as a new device and collect the same physical switch twice.
2. PHASE-087 adds case-normalised name/hostname identity checks on sequential and parallel collection paths. Redundant collection stops; distinct neighbours continue.
3. The reviewer reproduces `SWITCH-02 → SWITCH-01` in topology even though the collected seed node is `192.0.2.10`. Preserving the raw neighbour string has not met the required canonical back-edge criterion.
4. The reviewer rejects PHASE-087 and DD-016 despite the passing suite. The Architect agrees and defines the narrow PHASE-087A successor.
5. PHASE-087A maps the matching management address to the collected node. The edge becomes `SWITCH-02 → 192.0.2.10`, retaining `alias: SWITCH-01` and its `ip`.
6. The reviewer approves the topology change. Governance subsequently closes both phases together and records DD-016 Approved.

The original rejection remains historically correct. The later approval resolves that specific gap; it does not promise a collected node for every unsupported or uncollected neighbour.

## Significant defects and successful corrections

- **Neighbour platform propagation:** classification-derived neighbours could bypass the identity probe and receive generic Aruba commands on Aruba-CX hardware. PHASE-084 corrected the gate; the properly attributed PHASE-086 archive demonstrated the correct downstream profile and successful LLDP capture.
- **Duplicate physical-device collection:** different names for a matching address bypassed name-only revisit prevention. PHASE-087 supplies reviewed regression evidence for identity-based suppression.
- **Dangling alias topology target:** collection deduplication alone left the graph inconsistent. PHASE-087A supplies approved direct reproduction and topology regressions.
- **Evidence attribution/process error:** an older field archive was initially assessed against later changes. Direct archive discovery and provenance verification corrected the interpretation. This was a process lesson, not evidence that an already-fixed defect had recurred.
- **Credential exposure:** PHASE-041 stopped tracking live YAML credentials but explicitly left history cleanup and rotation outside its scope. PHASE-090 confirms publication preparation still needs that separate custody decision.

Discovery, classification, traversal, credential propagation, streaming and portable provenance are not reopened. New field evidence would be required to establish another technical defect.

## Lessons learned

Acceptance criteria must be checked against the final user-visible artefact. Testing only the collection path missed the topology requirement. A reviewer who can reject a plausible implementation is useful only when the rejection is grounded in a reproducible observation.

Build provenance must precede diagnosis. A correct analysis of an old binary can still produce an incorrect conclusion about current source. Commit titles are also insufficient: PHASE-090 found the reviewed code present as working-tree changes rather than in HEAD.

Human involvement was substantive. Operators supplied network context that the archives could not establish, challenged a failed file search and clarified that an additional advertised switch was not the missing rack device.

Absence of an identified neighbour does not establish physical absence, a disabled protocol or a parser defect. Unknowns need explicit labels, and enhancements need evidence rather than an invented failure.

Documentation and publication hygiene are engineering deliverables. Append-only history preserves learning but also preserves obsolete statements and sensitive data; a concise current entry point and a restricted archive are both necessary.

## Limitations and assessment

This is one evolving project with selected field captures, changing tools and no controlled comparison. There is no complete, comparable accounting of human time, agent time, token use, monetary cost or alternative implementation outcomes. The evidence does **not** support claims that AI is superior, faster or cheaper.

Hardware coverage is narrow. Broader vendor/version support, deeper live topology, production load, failure recovery under prolonged operation and complete physical discovery remain unvalidated. No new live collection was performed for PHASE-090.

**Experiment assessment:** successful demonstration of this human-directed engineering process and its ability to produce a working prototype, including a meaningful rejection/correction cycle. **MVP assessment:** achieved for the stated collection workflow. **Production assessment:** not established. See [closure](EXPERIMENT-CLOSURE.md) for baseline and publication status and [handover](CONTINUATION-HANDOVER.md) for continuation.
