PHASE:
CommandTimeoutSessionRootCause

FILES:
app/ssh_client.py
tests/test_ssh_client.py

ACCEPTANCE CRITERIA:
- Investigate why the initial `show version` timeout is followed by a cascade of `ssh_exception` failures against a dead Paramiko session (PHASE-032/034 field evidence).
- Determine whether the timeout itself kills the transport, or whether the device/transport was already degraded before the timeout.
- Document root-cause findings with reference to captured evidence fields (transport_active, original_transport_active, error_type).
- Any code change must be justified by the root-cause finding; investigation-only outcome is acceptable.

CONSTRAINTS:
- Do not modify recovery retry behaviour established by DD-007 without new field evidence.
- Do not modify provenance capture (DD-008).
- No vendor profile or paging changes unless root cause implicates them.

KNOWN RISKS:
- Root cause may be device-side (session limits, keepalive) and not fixable in this codebase.

OUTSTANDING RISKS:
- PHASE-034 evidence is inconclusive on causation; this phase may only narrow, not resolve, the hypothesis.

OPEN QUESTIONS:
- Is a second field bundle with packet-level or keepalive instrumentation needed to reach a conclusive answer?
