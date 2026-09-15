# Sanitisation report

Date: 14 September 2026.
Status: working-tree sanitisation completed; **the existing repository is not suitable for public publication with its current history and local artefacts**.

The recommended publication route is a fresh sanitised repository containing the reviewed source, tests, templates and documentation, with new Git history and rebuilt release packages. No repository was created or published by this pass.

## Scope and authority

The explicit repository-wide request authorised replacements in existing source/test/documentation and historical journal text, superseding the ordinary small-change and append-only restrictions for this pass. Phase chronology, architectural decisions, review verdicts, defect history and technical workflows were preserved. No technical defect was reopened.

Baseline HEAD is `c021e8e8882747502424d65dc34f52fdee2ded4b`. The starting tracked tree was clean. All changes are local working-tree edits: no staging, commit, push, history rewrite, remote visibility change or hosted release operation was performed. HEAD, branch and remote-tracking refs were verified unchanged. App-managed snapshot refs changed during the resumed session; these are excluded from that invariant and must also be excluded from publication.

The scan covered all 424 tracked paths and project-owned local text, configurations, outputs, review records, phase records and inspectable nested archives. The final residual scan inspected 968 loose project/artifact files, 1,639 readable text entries and 66 archives containing 11,371 member entries. These counts include nested duplicate evidence and exclude this report and temporary audit working files.

Installed environment directories were separately scanned: 5,291 files read, with identity-pattern candidates in 551. They were not rewritten as if they were project source. Third-party libraries, licences, protocol identifiers and vendor names were preserved where technically necessary. Binary/runtime and embedded Git boundaries are described below.

## Replacements performed

| Category | Replacement form | Occurrence operations |
|---|---|---:|
| Business/employer names | `<COMPANY>` | 110 |
| Customer references | `<CUSTOMER>` | 15 |
| Account/user identities | `<USERNAME>` | 111 |
| Email addresses | `person@example.com` | 61 |
| Device/host identities | `HOSTNAME-01 … HOSTNAME-20` | 8,753,976 |
| IPv4 addresses and IP-based paths | `192.168.2.x; 10.0.0.x` | 4,410,174 |
| IPv6 interface identities | `synthetic fe80:: values` | 56 |
| MAC addresses | `00:11:22:33:44:55 and distinct suffixes` | 120,585 |
| Serial numbers | `<SERIAL>` | 104 |
| Tenant reference | `<TENANT>` | 1 |
| Site/location names | `<LOCATION>` | 115 |
| Labelled contact/location fields | `person@example.com; <LOCATION>` | 88 |
| User-specific directory paths | `C:\Users\<USERNAME>\…` | 3 |
| Credential candidates and config placeholders | `<PASSWORD>` | 118 |

Counts cover the replacement passes, including repeated logs, filenames, archive members and nested copies; they are not counts of unique people or devices. Oversized logs were subsequently processed without truncation. There were 8 distinct large-log payloads, some approximately 89 MB, repeated across captures and nested bundles.

Specific personal-name components embedded in paths/accounts were removed by their enclosing username/path substitutions. There were no additional standalone personal-name replacements to count separately. No high-confidence provider API-key/token match or explicit asset-ID assignment was found in the covered project text; `<TOKEN>`, `<ASSET>` and `<PERSON>` remain the specified replacement forms if further candidates are identified. Domain-bearing email/account references were neutralised; the remaining internal-domain example form is `example.local`.

Two detected device-configuration credential literals, including ciphertext, were replaced in raw command evidence and its copied representations. Local YAML credentials and example-template values were replaced as well. This removes those literals from the covered working-tree text; it does not revoke or rotate anything on a device or service.

### Preserving technical meaning

- A single identical hostname/MAC would collapse different devices. Field-derived hostnames therefore use stable `HOSTNAME-nn` identities; 155 distinct MAC identities use the synthetic `00:11:22:33:xx:xx` family. Equality, inequality, alias relationships, case-normalisation tests and topology examples are preserved. Reserved zero/broadcast addresses remain protocol constants.
- IPv4 examples use the requested private example ranges; already synthetic `10.0.0.x` and documentation-range addresses remain. Four identifying IPv6 interface addresses were replaced with valid synthetic IPv6 values rather than changing their address family.
- Generic existing fixtures such as `seed-sw`, `SW01`, `admin` and deliberately distinct synthetic unit-test credentials remain where they are test data rather than a person's identity or a live credential.
- Prose placeholders are rendered visibly. When Windows filenames/path validation require legal characters, the placeholder is `USERNAME` or `HOSTNAME-nn` without angle brackets. No original user directory is retained in those examples.
- Vendor names, command syntax, platform/model/version identifiers, public technical documentation links, SSH algorithm identifiers, ASR rule IDs and agent/model role names remain where they explain the engineering behaviour. These are not treated as customer names.
- Phase and review records were retained. A historical acceptance criterion whose two original email values would otherwise collapse to the same placeholder was restated as “no original personal names or email addresses” to preserve its meaning.

## Files changed

The publication change set contains **63 existing tracked files plus this new report**. Application source and runtime entry points have no content changes. Seven test files changed their example identifiers or path fixtures. Two tracked configuration templates and the mailmap were sanitised.

- `.mailmap`
- `CONTINUATION-HANDOVER.md`
- `DEMONSTRATION.md`
- `EXPERIMENT-CLOSURE.md`
- `README.md`
- `RELEASE_NOTES.md`
- `config/devices.yml.example`
- `config/interactive_devices.yml.example`
- `docs/DESIGN-DECISION-REGISTER.md`
- `docs/FieldEvidence/PHASE-040-20260903-183540-bundle-findings.md`
- `docs/FieldEvidence/PHASE-046-20260903-fieldvalidation-findings.md`
- `docs/FieldEvidence/PHASE-058-20260905-185800-arubacx-lldp-format.md`
- `docs/FieldEvidence/PHASE-079-20260906-182850-fieldvalidation-findings.md`
- `docs/FieldEvidence/PHASE-083-20260906-2050-fieldvalidation-findings.md`
- `docs/FieldEvidence/PHASE-083-FT060920262050-DirectBundleVerification-20260907.md`
- `docs/FieldEvidence/PHASE-086-20260907-1340-secondhop-findings.md`
- `docs/FieldEvidence/PHASE-086-EvidenceRejection-20260907.md`
- `docs/HOWTO-PORTABLE.md`
- `docs/PROJECT-JOURNAL.md`
- `docs/Phases/IMPLEMENTED-PHASE-024-EmbeddedPythonRuntimeDistribution.md`
- `docs/Phases/IMPLEMENTED-PHASE-026-GitHistoryAuthorSanitisation.md`
- `docs/Phases/IMPLEMENTED-PHASE-040-FieldEvidencePostDiagnosticRefresh.md`
- `docs/Phases/IMPLEMENTED-PHASE-066-DeviceZipFilenameTruncationRemediation.md`
- `docs/Phases/IMPLEMENTED-PHASE-072-ArubaOSCXNeighborClassificationMetadataRemediation.md`
- `docs/Phases/IMPLEMENTED-PHASE-078-FieldValidationBuildRefresh-076A077ACheckpoint.md`
- `docs/Phases/IMPLEMENTED-PHASE-079-FieldValidationPost076A077A.md`
- `docs/Phases/IMPLEMENTED-PHASE-080-InteractiveDefaultCredentialPropagation.md`
- `docs/Phases/IMPLEMENTED-PHASE-082-FieldValidationBuildRefresh-081ACheckpoint.md`
- `docs/Phases/IMPLEMENTED-PHASE-083-FieldValidationPost081A.md`
- `docs/Phases/IMPLEMENTED-PHASE-087-DeviceIdentityDeduplicationByHostname.md`
- `docs/Phases/IMPLEMENTED-PHASE-087A-TopologyAliasBackEdgeRemediation.md`
- `docs/Phases/IMPLEMENTED-PHASE-091-ExperimentClosureBuildAndBaselineCapture.md`
- `docs/Phases/PHASE-023-ScriptBasedLaunchForManagedEndpoints.md`
- `docs/Phases/PHASE-023-TrustedLauncherDistributionModel.md`
- `docs/Phases/PHASE-024-EmbeddedPythonRuntimeDistribution.md`
- `docs/Phases/PHASE-025-PublicReleaseSanitisation.md`
- `docs/Phases/PHASE-026-GitHistoryAuthorSanitisation.md`
- `docs/Phases/PHASE-066-DeviceZipFilenameTruncationRemediation.md`
- `docs/Phases/PHASE-072-ArubaOSCXNeighborClassificationMetadataRemediation.md`
- `docs/Phases/PHASE-078-FieldValidationBuildRefresh-076A077ACheckpoint.md`
- `docs/Phases/PHASE-079-FieldValidationPost076A077A.md`
- `docs/Phases/PHASE-082-FieldValidationBuildRefresh-081ACheckpoint.md`
- `docs/Phases/PHASE-083-FieldValidationPost081A.md`
- `docs/Phases/PHASE-086-FieldValidationPost084-SecondHopTraversal.md`
- `docs/Phases/PHASE-087-DeviceIdentityDeduplicationByHostname.md`
- `docs/Phases/PHASE-087A-TopologyAliasBackEdgeRemediation.md`
- `docs/Phases/REVIEW-PHASE-075-FieldValidationPost072073.md`
- `docs/Phases/REVIEW-PHASE-078-FieldValidationBuildRefresh-076A077ACheckpoint.md`
- `docs/Phases/REVIEW-PHASE-079-080-081-FieldValidationClosureCredentialsAndProgress.md`
- `docs/Phases/REVIEW-PHASE-081A-IdentityProbeProgressAccuracyRemediation.md`
- `docs/Phases/REVIEW-PHASE-082-FieldValidationBuildRefresh-081ACheckpoint.md`
- `docs/Phases/REVIEW-PHASE-083-FieldValidationPost081A.md`
- `docs/Phases/REVIEW-PHASE-085-FieldValidationBuildRefresh-084Checkpoint.md`
- `docs/Phases/REVIEW-PHASE-087-DeviceIdentityDeduplicationByHostname.md`
- `docs/Phases/REVIEW-PHASE-087A-TopologyAliasBackEdgeRemediation.md`
- `docs/Wishlist.md`
- `tests/test_bootstrap.ps1`
- `tests/test_cli.py`
- `tests/test_discovery.py`
- `tests/test_normalization.py`
- `tests/test_orchestrator.py`
- `tests/test_parallel_collector.py`
- `tests/test_scope.py`
- `SANITISATION-REPORT.md` (new)

### Local ignored files and archives

In addition, 131 local paths were edited or renamed, including 24 top-level ZIP files. Six filesystem paths were renamed to match their sanitised IP-based names; member names inside ZIPs were also updated. Ignored files are still ignored and have not been force-added to Git.

Modified archives contain `SANITISATION-NOTICE.txt`. Notices in `field_tests/` and `dist/` and notes in the closure/release records distinguish sanitised derivatives from original evidence. Existing raw device logs were replaced, not shortened or discarded.

<details>
<summary>Local paths changed (sanitised final names)</summary>

- `.pytest_cache/v/cache/nodeids`
- `NetworkRecon.zip`
- `build/downloads/get-pip.py`
- `build/embedded/NetworkReconEngine/config/devices.yml.example`
- `build/embedded/NetworkReconEngine/config/interactive_devices.yml.example`
- `build/phase090-tests-20260908a/test_analysis_pipeline_preserv0/bundle_manifest.json`
- `build/phase090-tests-20260908a/test_bundle_manifest_message_c0/bundle_manifest.json`
- `build/phase090-tests-20260908a/test_bundle_manifest_message_c0/console.log`
- `build/phase090-tests-20260908a/test_cli_auto_detect_adopts_re0/bundle_manifest.json`
- `build/phase090-tests-20260908a/test_cli_default_scope_depth_o0/devices.yml`
- `build/phase090-tests-20260908a/test_cli_default_scope_depth_o0/output/console.log`
- `build/phase090-tests-20260908a/test_cli_scope_depth_passed_th0/devices.yml`
- `build/phase090-tests-20260908a/test_cli_scope_depth_passed_th0/output/console.log`
- `build/phase090-tests-20260908a/test_cli_scope_depth_without_t0/devices.yml`
- `build/phase090-tests-20260908a/test_cli_scope_depth_without_t0/output/console.log`
- `build/phase090-tests-20260908a/test_cli_target_device_limits_0/devices.yml`
- `build/phase090-tests-20260908a/test_cli_target_device_limits_0/output/console.log`
- `build/phase090-tests-20260908a/test_cli_target_device_selects0/devices.yml`
- `build/phase090-tests-20260908a/test_cli_target_device_selects0/output/console.log`
- `build/phase090-tests-20260908a/test_cli_target_device_without0/devices.yml`
- `build/phase090-tests-20260908a/test_cli_target_device_without0/output/console.log`
- `build/phase090-tests-20260908a/test_cli_unknown_target_device0/devices.yml`
- `build/phase090-tests-20260908a/test_cli_without_target_device0/devices.yml`
- `build/phase090-tests-20260908a/test_cli_without_target_device0/output/console.log`
- `build/phase090-tests-20260908a/test_configured_vendor_device_0/bundle_manifest.json`
- `build/phase090-tests-20260908a/test_default_recursion_enabled0/bundle_manifest.json`
- `build/phase090-tests-20260908a/test_default_recursion_enabled0/console.log`
- `build/phase090-tests-20260908a/test_device_full_override0/devices.yml`
- `build/phase090-tests-20260908a/test_device_fully_inherits_def0/devices.yml`
- `build/phase090-tests-20260908a/test_device_partial_override0/devices.yml`
- `build/phase090-tests-20260908a/test_embedded_malformed_placeh0/devices.yml`
- `build/phase090-tests-20260908a/test_embedded_malformed_placeh2/devices.yml`
- `build/phase090-tests-20260908a/test_inheritance_order_with_su0/devices.yml`
- `build/phase090-tests-20260908a/test_interactive_temp_inventor0/bundle_manifest.json`
- `build/phase090-tests-20260908a/test_interactive_temp_inventor0/console.log`
- `build/phase090-tests-20260908a/test_legacy_config_without_def0/devices.yml`
- `build/phase090-tests-20260908a/test_literal_values_remain_unt0/devices.yml`
- `build/phase090-tests-20260908a/test_load_default_credentials_0/devices.yml`
- `build/phase090-tests-20260908a/test_malformed_placeholder_wit2/devices.yml`
- `build/phase090-tests-20260908a/test_missing_checkpoint_file_i0/bundle_manifest.json`
- `build/phase090-tests-20260908a/test_missing_checkpoint_file_i0/console.log`
- `build/phase090-tests-20260908a/test_mixed_literal_and_substit0/devices.yml`
- `build/phase090-tests-20260908a/test_no_recurse_runs_flat_coll0/bundle_manifest.json`
- `build/phase090-tests-20260908a/test_non_recursive_cli_package0/bundle_manifest.json`
- `build/phase090-tests-20260908a/test_non_recursive_cli_package0/console.log`
- `build/phase090-tests-20260908a/test_non_recursive_cli_writes_0/bundle_manifest.json`
- `build/phase090-tests-20260908a/test_non_recursive_dry_run_doe0/bundle_manifest.json`
- `build/phase090-tests-20260908a/test_non_recursive_dry_run_doe0/console.log`
- `build/phase090-tests-20260908a/test_non_recursive_path_unchan0/bundle_manifest.json`
- `build/phase090-tests-20260908a/test_non_recursive_path_unchan0/console.log`
- `build/phase090-tests-20260908a/test_recursive_cli_creates_che0/bundle_manifest.json`
- `build/phase090-tests-20260908a/test_recursive_cli_creates_che0/console.log`
- `build/phase090-tests-20260908a/test_recursive_cli_dry_run_doe0/bundle_manifest.json`
- `build/phase090-tests-20260908a/test_recursive_cli_dry_run_doe0/console.log`
- `build/phase090-tests-20260908a/test_recursive_cli_invokes_orc0/bundle_manifest.json`
- `build/phase090-tests-20260908a/test_recursive_cli_invokes_orc0/console.log`
- `build/phase090-tests-20260908a/test_recursive_cli_invokes_orc0/devices.yml`
- `build/phase090-tests-20260908a/test_recursive_cli_passes_on_p0/console.log`
- `build/phase090-tests-20260908a/test_recursive_cli_resumes_fro0/bundle_manifest.json`
- `build/phase090-tests-20260908a/test_recursive_cli_resumes_fro0/console.log`
- `build/phase090-tests-20260908a/test_recursive_cli_uses_config0/bundle_manifest.json`
- `build/phase090-tests-20260908a/test_recursive_cli_uses_config0/console.log`
- `build/phase090-tests-20260908a/test_recursive_cli_uses_config0/devices.yml`
- `build/phase090-tests-20260908a/test_recursive_cli_verbose_log0/bundle_manifest.json`
- `build/phase090-tests-20260908a/test_recursive_cli_verbose_log0/console.log`
- `build/phase090-tests-20260908a/test_recursive_cli_verbose_log0/devices.yml`
- `build/phase090-tests-20260908a/test_recursive_cli_writes_anal0/bundle_manifest.json`
- `build/phase090-tests-20260908a/test_recursive_cli_writes_anal0/console.log`
- `build/phase090-tests-20260908a/test_recursive_cli_writes_bund0/bundle_manifest.json`
- `build/phase090-tests-20260908a/test_recursive_cli_writes_bund0/console.log`
- `build/phase090-tests-20260908a/test_recursive_cli_writes_devi0/bundle_manifest.json`
- `build/phase090-tests-20260908a/test_recursive_cli_writes_devi0/console.log`
- `build/phase090-tests-20260908a/test_run_recursive_cli_verbose0/bundle_manifest.json`
- `build/phase090-tests-20260908a/test_scoped_cli_streams_device0/bundle_manifest.json`
- `build/phase090-tests-20260908a/test_scoped_cli_streams_device0/console.log`
- `build/phase090-tests-20260908a/test_target_device_becomes_tra0/console.log`
- `build/phase090-tests-20260908a/test_target_device_with_topolo0/console.log`
- `build/phase090-tests-20260908a/test_valid_hostname_proceeds_t0/bundle_manifest.json`
- `build/phase090-tests-20260908a/test_valid_target_proceeds_to_0/bundle_manifest.json`
- `build/phase090-tests-20260908a/test_zip_bundle_distinct_prefi0/192.168.2.2`
- `build/phase090-tests-20260908a/test_zip_bundle_distinct_prefi0/192.168.2.2.zip`
- `build/phase090-tests-20260908a/test_zip_bundle_distinct_prefi0/192.168.2.2/summary.json`
- `build/phase090-tests-20260908a/test_zip_bundle_distinct_prefi0/192.168.2.241`
- `build/phase090-tests-20260908a/test_zip_bundle_distinct_prefi0/192.168.2.241.zip`
- `build/phase090-tests-20260908a/test_zip_bundle_distinct_prefi0/192.168.2.241/summary.json`
- `build/phase090-tests-20260908a/test_zip_bundle_preserves_ip_n0/192.168.2.241`
- `build/phase090-tests-20260908a/test_zip_bundle_preserves_ip_n0/192.168.2.241.zip`
- `build/phase090-tests-20260908a/test_zip_bundle_preserves_ip_n0/192.168.2.241/summary.json`
- `config/closure-demo.yml`
- `config/devices.yml`
- `demo_output/sample-cisco-router/summary.json`
- `demo_output/sample-juniper-router/summary.json`
- `dist/NetworkReconEngine-PHASE-085.zip`
- `dist/NetworkReconEngine-PHASE-091.zip`
- `dist/SANITISATION-NOTICE.txt`
- `field_output_040/bundle_manifest.json`
- `field_output_040/sample-aruba-switch.zip`
- `field_output_040/sample-aruba-switch/summary.json`
- `field_output_040/sample-aruba-switch/troubleshooting_bundle.json`
- `field_output_040/sample-cisco-router.zip`
- `field_output_040/sample-cisco-router/summary.json`
- `field_output_040/sample-cisco-router/troubleshooting_bundle.json`
- `field_output_040/sample-juniper-router.zip`
- `field_output_040/sample-juniper-router/summary.json`
- `field_output_040/sample-juniper-router/troubleshooting_bundle.json`
- `field_tests/FT050920262133.zip`
- `field_tests/FT060920260035.zip`
- `field_tests/FT060920261728.zip`
- `field_tests/FT060920261842.zip`
- `field_tests/FT060920261933.zip`
- `field_tests/FT060920262050.zip`
- `field_tests/FT070920261340.zip`
- `field_tests/Old/output1.zip`
- `field_tests/Old/output2.zip`
- `field_tests/SANITISATION-NOTICE.txt`
- `live_output/sample-aruba-switch.zip`
- `live_output/sample-aruba-switch/summary.json`
- `live_output/sample-cisco-router.zip`
- `live_output/sample-cisco-router/summary.json`
- `live_output/sample-juniper-router.zip`
- `live_output/sample-juniper-router/summary.json`
- `output/PHASE-034/bundle_manifest.json`
- `output/PHASE-034/interactive-device.zip`
- `output/PHASE-034/interactive-device/summary.json`
- `output/PHASE-034/interactive-device/troubleshooting_bundle.json`
- `output/interactive-device.zip`
- `output/interactive-device/summary.json`
- `output/phase068_demo/bundle_manifest.json`
- `output/phase068_demo/sample-cisco-router.zip`
- `output/phase068_demo/sample-cisco-router/build_provenance.json`
- `output/phase068_demo/sample-cisco-router/summary.json`

</details>

### Current derivative package checksums

These hashes identify the edited local files only. They are **not** build attestations or public-release approval. Earlier reports' checksums, sizes, source comparisons and provenance describe the pre-sanitisation artefacts.

| Local derivative | Bytes | SHA-256 |
|---|---:|---|
| `NetworkRecon.zip` | 34918871 | `68a47fd68defb155976c545c2ea07b5e252585be4cb7f9e4a4120a91712c0b44` |
| `dist/NetworkReconEngine-PHASE-085.zip` | 29409544 | `64293d767e6247ef0627ea73b6a096d7f417864142a0ae3a1faea0b255ef7824` |
| `dist/NetworkReconEngine-PHASE-091.zip` | 21179771 | `6d4e2d1485198beb4ed137311e3150ca345c3fe6faaaeeeb2192547ec0e38a6b` |

Rebuild distributable packages from the sanitised source. Do not upload these edited historical ZIPs as if they were the previously verified release.

## Verification

- Python suite: **354 passed, one established generic-profile fallback warning**. Two initial failures exposed IP filenames missed by a boundary pattern; both fixture expectations and filenames were corrected before the successful rerun.
- PowerShell test syntax and the affected valid-but-missing user-profile rejection case passed a direct check. The full Pester suite was not run: the available Pester 3.4 does not match its newer lifecycle syntax.
- Archive CRC checks passed across all 66 inspected archives, including nested archives. No record truncation or archive-member collision was required.
- 327 JSON entries parsed successfully. The existing deliberately corrupt checkpoint fixture under `build/` remains invalid by design; it is not a sanitisation failure.
- The final covered readable-text scan found **zero remaining matches for the identified source values**. This is a bounded candidate-based assessment, not proof that every possible free-text identity or secret is absent.
- No screenshots or raster-image files were found in the project-owned loose/archive scope, so there was no project screenshot metadata to strip. Runtime icons/binaries are outside that assertion.
- Git HEAD, branch and remote-tracking refs are unchanged; app-managed snapshot refs changed as noted in the completion verification. No Git-history rewrite or anonymisation is claimed.

Current normalised application/Python-test fingerprint:
`aa3a722f8b80609a9343086a7b5700191416f64d737ebaec8220a49a874b0d0d`.

Algorithm: sorted application paths followed by sorted test paths; SHA-256 each file after normalising CRLF to LF; concatenate POSIX relative path, NUL, lowercase hash and newline; SHA-256 that UTF-8 sequence. Historical fingerprints remain historical and need not match this sanitised test content.

## Remaining exposure and work not safely automated

| Area | Observed exposure / limit | Publication disposition |
|---|---|---|
| Reachable Git history | 120 commits assessed; identity matches in all 120 commit objects and 139 of 729 blob objects. One historical configuration blob still has a non-placeholder credential candidate | Do not publish this history unchanged |
| Dirty diffs and future provenance | Git diffs still contain the removed original values; a new dirty-tree provenance capture can copy those removed lines into a bundle | Build/capture public artefacts only from a clean sanitised baseline with new or fully cleaned history |
| Mailmap | Current file is a valid neutral example with no original mapping values | It cannot rewrite author/committer metadata, blobs or messages |
| Legacy `NetworkRecon.zip` | Contains an embedded `.git/`, including configuration, refs/logs and historical object data | Keep excluded. Editing that embedded history was not authorised by “do not rewrite history” |
| Compiled files and archived runtimes | 107 binary-entry identity-pattern matches; 3,953 matches among excluded runtime/embedded-Git members | Not automatically rewritten; replacing arbitrary bytes can corrupt code, signatures and metadata |
| Installed environments | 551 identity-pattern matches across virtual-environment metadata/caches | Exclude/recreate environments; do not copy them into a public tree or package |
| Unreadable directory | `.pytest_tmp/` denied access | Its contents could not be assessed; exclude it |
| Runtime library archives and other binary contents | Some runtime archives and 5 binary history objects were not exhaustively decoded | No comprehensive binary or third-party metadata clearance |
| Credentials | Working-tree literals were replaced; historical candidates remain and validity was not tested | Establish revocation/rotation separately if any remain usable |
| External copies | Remote-only refs, unreachable objects/reflogs, forks, backups, hosted assets and external field copies were not comprehensively audited | This local pass cannot remove or certify external copies |
| Retained technical detail | Topology, dates, firmware, models and workflow evidence remain intentionally | Correlation may still be possible; this is pseudonymisation, not a guarantee of irreversible anonymity |

The embedded Git data, compiled caches and inaccessible files were not deleted merely to produce a clean scan. No original-to-placeholder lookup is included in the report. Temporary audit snapshots and lookup files are removed after verification.

## Publication recommendation

**Existing repository, with its current Git history: NO — not suitable for public publication.**

**Sanitised source/documentation export: a reviewable candidate**, with passing regressions and no remaining identified-value matches in the covered text. Export the current edited working files, not an archive of the old HEAD (these edits are uncommitted). Perform a final review of the selected export, especially free-text evidence, licence notices and author settings.

**A fresh sanitised continuation repository is still preferred.** Initialise new history using an intentionally chosen public author identity. Include only the reviewed application, tests, dependency/build manifests, launchers, secret-free templates and sanitised documents. Preserve the sanitised SDLC/defect history as documents and an appropriate lineage note.

Exclude the original `.git/`, environments, caches, raw/output folders, local build folders and existing ZIPs. Rebuild release artefacts from the new source baseline and inspect their metadata/provenance before publishing. Keep the original experiment repository and remaining sensitive artefacts restricted.

If retaining the existing Git lineage is required instead, a **separately authorised history rewrite is required** for relevant file contents, paths, authors/committers and messages, followed by a full audit of rewritten refs and distribution copies. A mailmap-only author rewrite is insufficient. No rewrite was attempted here.

## Completion verification — 15 September 2026

The scan and regression evidence above were produced on 14 September. Final verification on 15 September rechecked the edited publication files, local links, archive hashes, Python syntax, unchanged application sources and empty Git index. HEAD and branch/remote-tracking refs remain at the saved baseline. App-managed `refs/codex/` snapshot references changed since the saved scan; the historical object counts above describe the earlier scan, not exhaustive clearance of these additional snapshots. They may retain identifying data and reinforce the requirement to exclude the entire original Git database. Task-created temporary audit snapshots, mappings and scripts were removed after verification. No commit, push, publication or Git-history rewrite was performed.

## Follow-up remediation — 15 September 2026

The user subsequently authorised a separate sanitised full-history copy. See [PUBLICATION-REMEDIATION-REPORT.md](PUBLICATION-REMEDIATION-REPORT.md) for the disposition of every remaining-exposure item, validation and publication boundaries. The earlier sections remain the record of the initial pass and continue to describe the original private repository; their no-history-rewrite statements do not describe the separately authorised review copy.
