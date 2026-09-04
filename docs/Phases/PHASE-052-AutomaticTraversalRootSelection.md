PHASE:
AutomaticTraversalRootSelection

FILES:
app/cli.py
tests/test_cli.py
tests/test_scope.py

ACCEPTANCE CRITERIA:
- When `--target-device` is supplied, it becomes the traversal seed directly; recursive collection scoping no longer requires a pre-existing `topology.json` to establish the initial scope (falls back to `[target_device]` and expands as neighbours are discovered during the run, consistent with existing `build_troubleshooting_scope()` semantics).
- Recursive collection defaults to enabled (equivalent to today's `--recursive` being on by default) when devices are configured; `--no-recurse` explicitly disables it.
- The existing `--recursive` flag is retained and accepted as a backward-compatible no-op/alias so existing scripts and tests are not broken without a migration path.
- `--scope-depth`, checkpoint/resume (`--checkpoint-file`), and `--max-concurrent` behaviour are unchanged.
- Full regression suite passes (`python -m pytest tests -q`).
- New tests cover: target-device-as-root without a prior `topology.json`, default-recursion-on with no flags supplied, `--no-recurse` opt-out, and backward-compatible `--recursive` usage still working.

CONSTRAINTS:
- No SSH, credential, provenance, or retry/recovery behaviour changes (app/ssh_client.py, app/provenance.py, app/config.py out of scope).
- No change to the `build_troubleshooting_scope()` traversal algorithm itself (app/scope.py); BFS/cycle-safety logic is already correct and out of scope.
- No command-profile or command-coverage changes (app/vendor_profiles.py out of scope).
- Do not restructure app/orchestrator.py or app/parallel_collector.py internals; only the CLI entry/default-selection logic in app/cli.py changes.
- Do not reproduce any field_tests/ hostnames, IPs, or other sensitive identifiers in source, tests, or documentation.

KNOWN RISKS:
- Changing the recursion default alters existing script/automation behaviour for callers that omit `--recursive`; requires a clear migration note in README/CLI `--help` text.
- Users relying on today's implicit single-device (non-recursive) run must adopt `--no-recurse` going forward.

OUTSTANDING RISKS:
- Running-config output completeness remains unverified (carried from PHASE-050; tracked separately as RunningConfigCaptureCompletenessValidation, not in scope here).
- ArubaOS-CX command coverage expansion remains deferred pending further field evidence (carried from PHASE-050, not in scope here).
- DD-007 remains inconclusively validated on real hardware (unrelated, carried risk).

OPEN QUESTIONS:
- Should `--recursive` become a deprecated no-op immediately (with a warning), or be silently accepted until removed in a later phase once `--no-recurse` is field-proven?
- Does automatic traversal rooting need any new safeguard (e.g., a device-count/confirmation prompt) before recursion is enabled by default, to avoid unexpectedly large collection runs against unfamiliar topologies?
