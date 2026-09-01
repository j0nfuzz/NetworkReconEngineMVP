# IMPLEMENTED-PHASE-029-SSHLegacyKexPortableSupport

PHASE:
PHASE-029-SSHLegacyKexPortableSupport

STATUS:
Implemented

FILES MODIFIED:
- app/ssh_client.py
  - Added `get_supported_kex_algorithms()` to expose Paramiko's current KEX set.
  - Added `_parse_name_list()` and `_extract_peer_kex_from_init()` to parse a raw SSH_MSG_KEXINIT packet.
  - Added `get_peer_kex_algorithms()` for a transport-level handshake that captures the peer's offered KEX list without authentication.
  - Added `_is_kex_error()` helper to unify KEX-failure detection.
  - Updated `explain_compatibility_error()` to include supported and peer-offered KEX algorithms plus guidance to use requirements-legacy.txt.
  - Updated `probe()` and `connect()` to invoke peer-KEX capture only on KEX failures and surface actionable diagnostics.
- build_portable.py
  - Added `--legacy` CLI flag.
  - `_build_embedded()` now accepts `legacy: bool` and installs `requirements-legacy.txt` when true, while copying both legacy and modern manifests into the bundle for reference.
  - `--legacy` is mutually exclusive with `--pyinstaller`.
- tests/test_cli.py
  - Added tests for KEX diagnostic messages, peer KEX packet parsing, and probe diagnostics.
- tests/test_build_portable.py
  - Added tests for `--legacy` selection and mutual exclusivity with `--pyinstaller`.

TESTS ADDED:
- tests/test_cli.py::test_ssh_client_explain_error_includes_kex_diagnostics
- tests/test_cli.py::test_ssh_client_explain_error_without_peer_kex_is_actionable
- tests/test_cli.py::test_ssh_client_extract_peer_kex_from_kexinit_packet
- tests/test_cli.py::test_ssh_client_probe_reports_kex_diagnostics
- tests/test_build_portable.py::test_main_defaults_to_embedded_modern_profile
- tests/test_build_portable.py::test_main_legacy_flag_selects_legacy_requirements
- tests/test_build_portable.py::test_main_pyinstaller_and_legacy_are_mutually_exclusive

DDR UPDATES:

DD-006

Decision:
Provide an opt-in legacy dependency profile for portable embedded builds via `--legacy`, installing requirements-legacy.txt instead of requirements.txt.

Reason:
Field testing observed a KEX negotiation failure against a legacy SSH peer; Paramiko's modern profile no longer enables the required SHA1-based KEX algorithms, and the embedded runtime bundle previously had no mechanism to use the existing legacy profile.

Status:
Proposed

Approver:
GPT Reviewer

Date:
2026-09-01

Phase:
PHASE-029-SSHLegacyKexPortableSupport

RISKS INTRODUCED:
- Peer KEX probe performs an additional TCP handshake; unreachable hosts may experience an extra timeout delay.
- Legacy profile enables known-weak algorithms; restricted to explicit opt-in only.
- Parsing the peer's raw SSH_MSG_KEXINIT depends on Paramiko internals (remote_kex_init); future Paramiko versions may change the attribute shape, degrading diagnostics to "(could not be obtained)".

RISKS RESOLVED:
- KEX failures now report both supported and peer-offered algorithms, making the root cause actionable.
- Portable embedded builds can target legacy SSH devices without replacing Paramiko or adding new dependencies.
- Default modern-device behaviour is unchanged.

OPEN ISSUES:
- Whether 192.0.2.30 will negotiate successfully under the legacy profile remains unconfirmed until field-tested.
- Open question from phase file: should the embedded bundle ship both profiles side-by-side or remain single-profile-per-build? Current implementation remains single-profile-per-build with `--legacy` opt-in.
