PHASE:
CommandTimeoutSessionRootCause

STATUS:
Implemented

FILES MODIFIED:
- app/ssh_client.py
  - Added `_channel_state()` and `_transport_state()` static helpers to capture non-blocking Paramiko diagnostics.
  - Extended timeout, ssh_exception, and success result dictionaries with `transport_state` and `channel_state`.
  - No changes to timeout values, timeout handling, SSH negotiation, recovery logic, retry logic, vendor detection, or collection sequencing.
- tests/test_ssh_client.py (new)
  - 5 tests verifying `channel_state` and `transport_state` appear on timeout, ssh_exception, and success paths, plus graceful handling of missing channels/clients.

TESTS ADDED:
- tests/test_ssh_client.py (5 tests)

DDR UPDATES:
UNCHANGED DD:DD-008

RISKS INTRODUCED:
- Additional result fields increase payload size; acceptable for evidence-quality improvement.
- Paramiko channel/transport introspection can raise exceptions on some transports; helpers swallow exceptions and return error diagnostics.

RISKS RESOLVED:
- Future field bundles will include channel and transport snapshots around timeout and ssh_exception events, narrowing the root-cause hypothesis from PHASE-032/034.

OPEN ISSUES:
- A second field bundle may still be needed to determine whether the timeout itself kills the transport or the transport was degraded beforehand.
