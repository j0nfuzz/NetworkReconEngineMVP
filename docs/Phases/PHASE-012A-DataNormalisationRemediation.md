PHASE:
DataNormalisationRemediation

FILES:
- app/normalization.py
- tests/test_normalization.py

ACCEPTANCE CRITERIA:
- `_find_cisco_interface_errors()` evaluates all supported error counters (`input errors`, `output errors`, `CRC`) present on an interface's detail line(s), not just the first regex match.
- An interface is flagged whenever any one counter is nonzero, e.g. `0 input errors, 678 CRC` must include the interface.
- Interfaces with all-zero counters remain excluded (no regression on existing passing case).
- `build_device_summary()` output shape and all other fields (hostname, vendor, model, version, uptime_days, cpu, memory, routes, arp_entries) are unchanged.
- Add regression test for the exact false-negative case (`0 input errors, 678 CRC`) and a mixed-counters case confirming only genuinely-zero interfaces are excluded.

CONSTRAINTS:
- No new dependencies.
- No changes to `Device`, `DeviceBundle`, `execute_device_collection()`, or CLI signatures.
- Deterministic regex/keyword parsing only.
- Do not wire into `cli.py` (still out of scope, per PHASE-012).

KNOWN RISKS:
- None beyond those already carried from PHASE-012 (Cisco format drift; unsupported vendors return defaults).

OUTSTANDING RISKS:
- CLI integration of `build_device_summary()` remains deferred.
- Single-seed recursion and plaintext checkpoint/credential limitations carried from PHASE-011/011A remain unresolved.

OPEN QUESTIONS:
- None.
