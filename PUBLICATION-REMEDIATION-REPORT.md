# Publication remediation report

Date: 15 September 2026.

The remaining-exposure assessment has been remediated in a **separate, sanitised full-history review copy**. All 120 original commits remain in sequence, with neutral author/committer identities and sanitised historical file contents. New local commits record the reviewed working tree and verification. The original repository and its remote remain private and unchanged in history; they must not be published as-is.

The user authorised preparation of this separate history copy and requested removal/replacement of credential values, rather than rotation on live systems. Nothing was pushed or published. No live credential was tested.

## Disposition of every remaining-exposure item

| Original item | Remediation and evidence | Remaining boundary |
|---|---|---|
| Reachable Git history | Reconstructed 120 commits, preserving chronology, parent relationships and technical records; replaced author/committer identities with `PERSON <person@example.com>` and sanitised historical blobs and archive contents. Imported the final result into a new object database, so intermediate objects and original reflogs are absent. | Original history is deliberately retained privately. An old nested `audit` checkout was stored as a gitlink, not files; one referenced commit is unavailable. Its historical location now contains an explanatory notice. Unavailable external content cannot be recovered or certified. |
| Dirty diffs and future provenance | Release builds now fail before staging unless Git confirms a clean checkout. The rebuilt package records `dirty=false` and an empty patch. | Build from the sanitised copy. The original checkout's diffs still contain removed originals and must stay private. Ordinary provenance capture behaviour remains available for private development. |
| Mailmap | The review copy has neutral commit metadata, not just a mailmap display override. Its local Git author configuration is neutral and no remote is configured. | Choose an appropriate public author identity before future commits. |
| Legacy archive with embedded Git | Historical ZIPs were reconstructed, retaining project source, tests, documentation and example output while excluding embedded Git, environments and caches. Derivative notices explain the changed bytes. | Original private ZIPs are preserved separately and are not publication artefacts. Their old hashes are historical evidence only. |
| Compiled files and archived runtimes | Removed generated caches from historical derivative archives and rebuilt the current runtime from official CPython and the declared dependencies. Release packaging excludes source caches and installer launchers that embed absolute interpreter paths. | Third-party binaries retain their upstream metadata, signatures and required attribution; arbitrary byte replacement was not used. |
| Installed environments | Original virtual environments are excluded from the review copy. The new runtime has freshly installed dependencies. | The original private environments remain local and must not be copied into a publication. |
| Unreadable cache directory | The inaccessible original `.pytest_tmp` directory is excluded. Validation used new temporary directories outside the publication copy. | No claim is made about the inaccessible original contents. They are not needed by the project or publication. |
| Runtime archives and binary contents | Recursively checked the rebuilt ZIP and embedded standard-library archive, including readable byte strings in binary members. Checked archive CRCs and safe extraction. Historical reconstructed archive contents were also scanned. | These checks establish absence of the identified project values in covered representations; they do not prove absence of every conceivable encoded value. |
| Credentials | Replaced the historical configuration candidate, remaining credential literals and ordinary test passwords with placeholders. Distinct placeholders retain default/device override tests. Final project/history scans found no remaining candidates under the documented checks. | Environment-variable references and deliberately malformed reference fixtures remain as test syntax. No live credentials were accessed or rotated, as requested. |
| External copies | Queried the configured GitHub repository: private; one branch matching the original local release; no releases, listed forks, workflow artefacts or workflow caches. The review copy has no remote. | Backups, downloads, unlisted copies, hosted retention and inaccessible external repositories cannot be erased or certified by this local task. Keeping the original remote private remains necessary. |
| Retained technical detail | Preserved workflows, phase/review chronology, defect history, topology relationships and vendor/model/firmware explanations. Replaced direct project identities and credential values. | Correlation from intentionally retained technical detail remains possible. Complete irreversible anonymity would conflict with preserving those records. This residual is not claimed to be eliminated. |

## Validation

- **359 tests passed**, with the established generic-profile fallback warning, in the review copy using the rebuilt runtime and its freshly resolved dependencies.
- Both extracted Windows launchers completed their `--help` checks successfully.
- The runtime archive and its embedded library archive passed CRC checks and safe-path extraction checks.
- Runtime scan coverage: 2,463 entries including two archives, 1,827 text entries and 634 binary entries. No confirmed project-identity matches remained in the covered text/ASCII/UTF-16 representations.
- Broad scanner matches were reviewed: three machine-code byte sequences resembled generic hostname patterns, and three upstream dependency files contained common private-address examples. These are not project-origin identities; upstream code was preserved.
- Historical/project scanning includes commit metadata, current tracked files and recursively inspected ZIP members. Standard SSH algorithm identifiers containing `@` are protocol names, not email exposures. Empty values, explicit placeholders, type annotations and deliberately malformed environment-reference test inputs are not credential values.
- Git object integrity, parent-count preservation, clean review-copy status and absence of original/unreachable objects are checked before delivery. The original source HEAD and index are checked separately.

The rebuilt ZIP is 20,637,984 bytes. Its SHA-256 is:

`0d0fe9682e8ced2ffcae33ade8f5c1fd3bbb255748049608b2afc2bc9d21e4b3`

It was built from clean review-copy commit `a305b9e8359cb0c2f4ef736994a0e994d21afef6`. Subsequent verification commits change documentation and test isolation only; application and packaging inputs are unchanged. Its embedded provenance describes that actual build commit.

## Publication recommendation

Use the sanitised full-history copy and the newly rebuilt package for publication review. Starting new history is no longer required to address the **identified local historical exposures**: the separate rewritten history preserves the experiment's lineage and technical records.

Do not change the original repository to public or publish its old archives. The remaining boundaries above—unknown external copies, unavailable audit checkout content and correlation from retained technical detail—prevent a claim that every possible exposure has been eliminated. No publication or replacement of the original remote has been performed.

Temporary identity mappings, intermediate history copies, extracted runtime files and temporary test directories created by this remediation are removed after verification. The retained deliverables are the sanitised review repository, its rebuilt runtime ZIP, a Git history bundle, a source export and this report.
