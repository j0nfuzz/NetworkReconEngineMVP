PHASE:
DataNormalisation

FILES:
- app/normalization.py
- tests/test_normalization.py

ACCEPTANCE CRITERIA:
- New `build_device_summary(bundle: DeviceBundle) -> dict` produces a vendor-independent `summary.json`-shaped dict (hostname, vendor, model, version, uptime_days, cpu, memory, routes, arp_entries, interface_errors) derived only from already-collected `bundle.raw_outputs`/`bundle.summary`.
- Missing/unparseable fields default to `None` or `[]`; function never raises on absent data.
- Raw evidence (`bundle.raw_outputs`) remains untouched and fully retained (DD principle: raw evidence retention).
- No SSH calls, no new commands, no changes to collection logic.
- Tests cover: full-data parse, missing-field defaults, and at least one real vendor sample (cisco) reusing existing collector fixtures/output patterns.

CONSTRAINTS:
- No new dependencies.
- No changes to `Device`, `DeviceBundle`, `execute_device_collection()`, or CLI signatures this phase.
- Deterministic regex/keyword parsing only, consistent with DD-002/DD-003 approach.
- Do not wire into `cli.py` yet (kept out of scope to keep the change small and reviewable).

KNOWN RISKS:
- Vendor output format drift could cause silent `None`/default values rather than errors (acceptable for PoC; documented, not solved, this phase).

OUTSTANDING RISKS:
- CLI integration of `build_device_summary()` output is deferred to a future phase.
- Single-seed recursion and plaintext checkpoint/credential limitations carried from PHASE-011/011A remain unresolved.

OPEN QUESTIONS:
- None.
