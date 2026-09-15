# Continuation handover

**Publication follow-up:** a sanitised continuation repository remains recommended. Export the reviewed current source and documents without the existing Git history or local runtime/output folders; rebuild release packages. See [SANITISATION-REPORT.md](SANITISATION-REPORT.md).

PHASE-090 closes development in the experiment repository. The experiment and scoped MVP are complete; continuation is optional future work in a **separate repository**. No new repository has been created and no destination URL has been invented.

## Complete

The supported seed-to-neighbour collection workflow is field demonstrated. Platform-aware downstream collection works on the observed Aruba-CX hardware. Identity deduplication and canonical alias back-edges are approved through PHASE-087/087A reviews and regression evidence. DD-016 is Approved; the original rejection remains historical. The current suite passes 354 tests.

The experiment report, corrected README, reproducible demonstration, closure baseline and release preparation form the endpoint. Read [EXPERIMENT-CLOSURE.md](EXPERIMENT-CLOSURE.md) for the precise evidence boundary and the source baseline captured by the user-authorised closure commit.

## Not complete

Routine production deployment validation, broad vendor/firmware field coverage, estate-scale reliability, complete physical inventory, an identified additional rack switch, a post-fix live archive, a new closure package, public publication clearance and an annotated source tag have not been established. The commit titled `Experiment Complete 2026-09-08` captures the reviewed source baseline.

DD-017 remains **Proposed**, pending reviewer consideration. Closing the experiment neither approves that proposal nor makes MAC-based enrichment an implementation requirement.

`CONTRIBUTING.md` and `RELEASE_NOTES.md` did not exist at assessment start. PHASE-090 creates release notes; this handover provides the contribution boundary until the continuation repository adopts its own contributor guide.

## Where development continues

Suggested repository name: **NetworkReconEngine-Continuation** (proposal, not an existing service location).

Prefer a new repository with a sanitised initial history and explicit lineage to the restricted experiment baseline. Preserve the original complete history in the experiment archive. A normal fork retains historical exposures, so use one only if the continuation is intentionally restricted and its custodian accepts that history.

Suggested layout:

```text
app/                         reviewed collector source
tests/                       sanitised deterministic fixtures and regressions
config/                      secret-free *.example inventories
docs/
  architecture/              current accepted decisions and schema contracts
  evidence/                  sanitised evidence index and findings
  roadmap/                   classified continuation backlog
  operations/                deployment, trust and recovery guidance
README.md                    product scope, evidence levels and quick start
CONTRIBUTING.md              workflow, review and evidence requirements
RELEASE_NOTES.md             continuation release history
EXPERIMENT-LINEAGE.md        original closure reference and exact source baseline
```

Select source, tests, dependency/build manifests, launchers and applicable licence notices deliberately. Do not copy `.git`, credentials, live output, raw field archives, provenance patches or existing ZIPs into a public continuation tree. Review test fixtures and governance documents as well as configuration. Record any sanitisation changes and validate the imported source.

The actual destination and maintainer are **unassigned**. Until created, this handover is the authoritative continuation entry point; it does not authorise further work in the experiment repository.

## Continuation backlog

| Item | Classification | Disposition and activation |
|---|---|---|
| [PHASE-089: SW3 discovery evidence assessment](docs/Phases/PHASE-089-SW3DiscoveryEvidenceAssessment.md) | Research; prerequisite evidence for an Enhancement | Moved to continuation backlog, not executed. Recommended first optional activity after a maintainer accepts it |
| [PHASE-088: MAC-table observations](docs/Phases/PHASE-088-MacAddressTableTopologyEnrichment.md) | Enhancement; deferred Roadmap | Moved to continuation backlog. Activate only if PHASE-089 supports value, an architect selects it and DD-017/schema semantics receive review |
| More vendor/version and post-fix live captures | Research | Choose a bounded hardware matrix; preserve provenance and distinguish field from mocked evidence |
| Packaging, dependency locking, credentials/trust, recovery and operating limits | Roadmap | Define production acceptance evidence before claiming routine deployment readiness |
| MAC/ARP/interface correlation, LACP, STP and routing relationships | Roadmap | Retain source and uncertainty; distinguish forwarding reachability, physical links and Layer-3 relationships |
| Identity across disjoint management addresses | Research | Quantify actual cases before proposing an identity model change |
| Comparative AI cost/time/quality study | Research | Define a controlled baseline, human effort accounting and comparable budgets before making comparative claims |

The phase files remain at their original paths to preserve links. Their status is changed to continuation backlog; they are not active implementation orders. This supersedes earlier recommendations to execute PHASE-089 next in this repository and earlier PHASE-088 activation language.

PHASE-089 may validly conclude **unresolved**, identifying missing operator-confirmed identity/attachment or a bounded supplementary capture. Missing SW3 visibility is not automatically a defect. PHASE-088 must not infer adjacency or trigger traversal from MAC/OUI alone.

## Handover and acceptance

```text
PHASE:
PHASE-090 — Experiment Closure and Continuation Handover

FILES:
README.md; EXPERIMENT-REPORT.md; DEMONSTRATION.md;
EXPERIMENT-CLOSURE.md; CONTINUATION-HANDOVER.md; RELEASE_NOTES.md;
docs/HOWTO-PORTABLE.md; docs/PROJECT-JOURNAL.md;
docs/Phases/PHASE-088-MacAddressTableTopologyEnrichment.md;
docs/Phases/PHASE-089-SW3DiscoveryEvidenceAssessment.md

ACCEPTANCE CRITERIA:
A new reader can understand the experiment, reproduce the demonstrated
workflow, distinguish evidence from limitations, and locate continuation.
All five principal deliverables exist; source behaviour is unchanged.

CONSTRAINTS:
Freeze experiment development. Do not reopen approved defects without new
field evidence. Continuation work requires selection in a separate repository.

KNOWN RISKS:
Historical sensitive-data exposure; narrow live validation; unresolved identities.

OUTSTANDING RISKS:
No annotated release tag or new package;
publication clearance and continuation ownership are pending.

OPEN QUESTIONS:
Who will own the restricted baseline and the continuation repository?
What production scope and evidence budget should continuation adopt?
```

Custodial sequence after the authorised closure commit/push: verify its exact source baseline; preserve local raw evidence separately; annotate the recommended experiment tag; archive the original repository; then create and review a sanitised continuation baseline if development is selected. These are release/ownership actions, not renewed product remediation.

Contribution rule: proposed future work belongs in the continuation backlog with a category, evidence, owner and acceptance criteria. Keep completed-phase records intact and carry forward accepted decisions only with their actual status.
