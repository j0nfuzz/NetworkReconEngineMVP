PHASE:
PortableDistributionPackagingRemediation

FILES:
build_portable.py
docs/HOWTO-PORTABLE.md
README.md

ACCEPTANCE CRITERIA:
- Phase record explicitly accepts PyInstaller onedir as the approved packaging format (supersedes the single-file requirement in PHASE-021).
- build_portable.py produces one distributable artefact (a zip of dist\NetworkDeviceDiagnostics) as its final build output, not just an unpackaged folder.
- README.md and HOWTO-PORTABLE.md describe distributing the single zip artefact rather than a raw folder.
- No change to CLI arguments, launch experience, or config-based workflow.

CONSTRAINTS:
- Do not reattempt onefile packaging.
- Do not add interactive prompting or change how device details are supplied.
- Files listed above only.

KNOWN RISKS:
- None (packaging-contract and distribution-format change only).

OUTSTANDING RISKS:
- Unsigned executable may still be quarantined by other endpoint protection products.
- --max-concurrent ceiling (10) remains non-configurable; carried from PHASE-019.

OPEN QUESTIONS:
- None for this phase; engineer-launch experience (device-detail prompting without a config file) is deferred to a separate future phase.
