PHASE:
SSHLegacyKexPortableSupport

FILES:
app/ssh_client.py
build_portable.py

ACCEPTANCE CRITERIA:
- probe()/connect() failure messages include the peer's offered KEX algorithms and Paramiko's supported set, not just a generic explanation.
- --pyinstaller/--legacy embedded-runtime build option installs requirements-legacy.txt instead of requirements.txt.
- Existing 146 tests continue to pass; no behaviour change for already-working modern-KEX devices.

CONSTRAINTS:
- No new dependencies; reuse requirements-legacy.txt already in the repo.
- Do not change host-key or auth logic.
- Keep default embedded build on the modern profile; legacy is opt-in via existing flag pattern.

KNOWN RISKS:
- Paramiko may not expose the peer's offered KEX list without deeper Transport inspection; diagnostic accuracy depends on what paramiko's exception/negotiation state exposes.
- Legacy paramiko/cryptography versions carry known-weak algorithms; must document security trade-off in HOWTO-PORTABLE.md scope note (doc change only if needed later).

OUTSTANDING RISKS:
- Whether 192.168.21.30 negotiates only via an algorithm legacy paramiko also lacks remains unconfirmed until diagnostics are field-tested (2026-09-01).

OPEN QUESTIONS:
- Should the embedded bundle ship both profiles side-by-side, or remain single-profile-per-build as today?
