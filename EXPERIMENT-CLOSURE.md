# Experiment closure — PHASE-090

Assessment date: 8 September 2026.

**Closure decision: the engineering experiment is complete and the scoped MVP is achieved.** The result is a working prototype. Routine production deployment readiness and a publishable release are not established. PHASE-087/087A stay closed; DD-016 stays Approved. PHASE-090 adds documentation and release preparation only.

## Final repository state

Commit follow-up, 8 September 2026: the user authorised staging the outstanding implementation, tests and documentation, committing as `Experiment Complete 2026-09-08`, and pushing to the existing private origin. The closure commit containing this update captures that reviewed source and its supporting records. The table below preserves the **initial assessment** state; it is not the post-commit status. No annotated tag, history rewrite, release upload or hosted archival is included.

| Item | Recorded state |
|---|---|
| HEAD at assessment | `33bfd9709b4301e0f2191197af83907451486028` |
| Actual reviewed implementation | HEAD **plus existing working-tree changes**; the commit title does not establish that the fixes are committed |
| Existing modified production files | `app/orchestrator.py`, `app/parallel_collector.py`, `app/topology.py` |
| Existing modified tests | `tests/test_cli.py`, `tests/test_orchestrator.py`, `tests/test_parallel_collector.py` |
| Other pre-existing state | Modified DDR, journal and combined closure; untracked field findings, implementation reports and PHASE-088/089 definitions |
| PHASE-090 changes | Ten documentation paths: five principal deliverables, release notes, portable guide, two backlog definitions and journal |
| Runtime changes during PHASE-090 | None; source/test fingerprint checked before and after |
| Git/release actions | No implementation commit, tag, push, release upload, history rewrite or hosting-side archive action performed |

The freeze is a **development disposition**. A checkout of the closure commit reproduces the reviewed source; a checkout of the initial assessment HEAD alone does not. Identify the closure commit with `git log -1 --format=%H --fixed-strings --grep="Experiment Complete 2026-09-08"`. Preserve local raw evidence separately; ignored files are not part of this source baseline.

Fingerprint of all 38 `app/*.py` and `tests/*.py` files:
`a612766725791f703a07b949ea2b724b97f86069dd3acef8eab82572caa46d65`.

Algorithm: list application paths sorted, then test paths sorted; calculate SHA-256 of each file's bytes; concatenate each repository-relative POSIX path, NUL, lowercase file hash and newline; SHA-256 the UTF-8 concatenation. This identifies source/test content, not the dependency environment or a distributable archive.

| Critical source file | SHA-256 of assessed bytes |
|---|---|
| `app/orchestrator.py` | `8f545535b8c6ade7016b7edf0010c3c38fc8638fc812a218d2d5380769975c4a` |
| `app/parallel_collector.py` | `abe832cc4468aed863b8c1a8abee0c234d3696c4d67ea3fae058e88576b2ab24` |
| `app/topology.py` | `2cc8f59ded8f8d97b82e88f1de051948f691c142cf980f4071c282ca7f49b838` |

## MVP determination and supported capabilities

The MVP is the demonstrated seed → supported neighbour → correctly profiled collection → usable evidence package workflow. PHASE-086 establishes that workflow for two distinct physical Aruba-CX switches. Three collection records in that archive include one redundant seed alias; they are not three physical switches.

Working-tree capabilities include LLDP/CDP discovery, deterministic classification, recursive traversal by default, credential inheritance, progress and incremental artefacts, raw evidence, structured summaries, troubleshooting bundles, topology, checkpoints, bounded parallel target collection and portable provenance. PHASE-087/087A add reviewed identity deduplication and canonical alias back-edges.

The supplied field archive SHA-256 is
`4bd6adfb7cdab70549473b8fa1a563e5a56465928766e876b684ae1d9dd4972e`.
All three provenance records identify clean build
`462bf4366d0121b17209856059df9258bc428309`.
Direct inspection during PHASE-090 reconfirmed three summaries, 11 commands and zero failed commands each, with LLDP counts 10, 10 and 4.

That archive predates PHASE-087/087A. The approved review and deterministic reproduction establish the subsequent fixes. There is no supplied post-fix live archive. This qualification preserves historical accuracy without reopening accepted phases.

## Validation performed for closure

- Re-ran the current full regression suite: **354 passed, one established generic-profile fallback warning**.
- Ran the documented recursive dry-run packaging example and asserted its output files and simulated status. Provenance was disabled for this local smoke check to avoid copying the pre-existing sensitive tracked diff into demonstration output; normal provenance remains covered by the regression suite.
- Ran the documented synthetic topology example and checked the exact canonical back-edge and retained alias.
- Checked the five principal deliverables, internal file links, documented CLI options and unchanged application/test fingerprint.
- Reviewed documentation, reachable local Git history and selected local archives for obvious sensitive-data exposure.

Environment: bundled CPython 3.12.14 with the existing `.venv/Lib/site-packages` dependencies. The local `.venv` launcher referenced a missing interpreter. The initial test invocation also encountered access errors clearing the shared pytest temporary directory; a fresh `--basetemp` and `-o addopts=` resolved this environmental issue. No application change was needed.

No live SSH run, new portable build, deployment, security certification or independent human usability trial was performed. The release notes contain the repeatable validation command.

## Limitations and outstanding opportunities

- Field coverage is narrow; multi-vendor profiles and parallel collection are not equivalent to all-platform field validation.
- The unresolved additional rack switch has no positively established identity in the relevant downstream capture. Its attachment and visibility remain unknown; no new defect is established.
- LLDP/CDP discovery is not exhaustive physical inventory. Unknown or uncollected neighbours may remain edge targets without nodes.
- Identity matching covers the observed shared-address/name cases. Multiple disjoint management identities remain an accepted limitation.
- Checkpoint and parallel regressions do not establish estate-scale or prolonged failure-recovery behaviour.
- Default trust policy, credential lifecycle, dependency reproducibility and operating limits need continuation assessment before production claims.
- The bootstrap's generated inventory lacks default credentials; the demonstration uses the direct CLI/explicit defaults.
- Provenance excludes live YAML but tracked diffs can still expose sensitive content, and untracked implementation files are not captured by that patch.
- Broader discovery, correlation, stronger identity reconciliation and operational packaging are Enhancement, Roadmap or Research opportunities in the continuation handover.

## Sensitive-data and publication review

**Publication disposition: not cleared for public release.** This is a bounded exposure review, not a comprehensive secret scan or an assertion about whether any credential is currently valid.

| Area reviewed | Finding | Disposition |
|---|---|---|
| Current tracked documentation and tests | Exact matches to field-derived identity values appeared in 31 tracked paths, including the DDR, journal, phase/review documents and tests | Preserve restricted history; sanitise selected material before external publication |
| Reachable local history | 118 reachable commits; 698 candidate text blobs inspected. Field-identity matches occurred across 36 historical paths | Current-tree cleanup alone cannot sanitise history |
| Historical configuration | Non-placeholder credential candidates remain in historical `config/devices.yml`; PHASE-041 already documents this exposure and explicitly excludes history rewrite | Custodian must establish rotation/invalidity and separately authorise any history cleanup; no claim that rotation occurred |
| Current ignored material | Raw field captures, generated outputs and live YAML are deliberately local and ignored | Git ignore rules do not make copied folders or ZIPs safe |
| Root `NetworkRecon.zip` | Two configuration members contain credential-like non-placeholder candidates; no runtime provenance or current alias fix found in inspected members | Treat as restricted legacy material, not a release candidate |
| `dist/NetworkReconEngine-PHASE-085.zip` | Runtime provenance exists; inspected source lacks the later alias fix. No selected credential/identity-pattern matches were found | Historical build only; absence of these matches is not a publication clearance |
| New closure examples | Synthetic names and documentation-range IPs; no raw field identifiers copied into the new examples | Suitable as reviewable examples, subject to the overall release review |

The historical scan covered text blobs with `.md/.py/.txt/.json/.yml/.yaml/.log` suffixes reachable through local `--all` refs. Exact identity matching used a small set from the supplied archive; credential checks were heuristic. Archive inspection covered selected text members no larger than 2 MB and did not recursively expand nested ZIPs. Unreachable objects, reflogs, remote-only refs, binary contents, all possible secrets and the validity of credentials were not exhaustively assessed.

No raw values are reproduced here. Existing history and evidence were not rewritten or redistributed. This finding is release/custody work, not grounds to reopen closed collection defects.

## Baseline, tag and archive recommendation

Recommend the annotated tag **`experiment-complete-2026-09`**, pointing to the exact reconciled closure commit, with [RELEASE_NOTES.md](RELEASE_NOTES.md) as its annotation/release description.

The subsequent explicit commit/push authorisation supersedes PHASE-090's earlier documentation-only commit boundary. The closure commit captures the reviewed implementation, tests and supporting records. After verifying its hash and source fingerprint, a custodian may apply the separately recommended annotated tag. Tagging is not part of this commit/push request.

Recommend **archiving this experiment repository after baseline capture**, with restricted access appropriate to its history. Keep raw evidence in a controlled store and retain its attribution. Do not make public archival a prerequisite for declaring the engineering experiment complete.

Continue development in a separate repository under the structure and backlog in [CONTINUATION-HANDOVER.md](CONTINUATION-HANDOVER.md). Do not activate PHASE-088/089 here.

## Closure criterion

The README explains the experiment and actual defaults; the report explains the method and evidence; the demonstration supplies runnable offline examples and a bounded live lab procedure; this document states the exact baseline and limitations; the handover identifies where future work starts. These are the five PHASE-090 deliverables.

**Experiment complete. Scoped MVP achieved. Production readiness unclaimed. The user-authorised closure commit captures the reviewed source baseline; annotated tagging, public publication clearance and hosted archival remain separate custodial actions.**
