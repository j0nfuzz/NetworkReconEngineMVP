# Release notes — experiment-complete-2026-09

**Prepared release; tag not created.** Date: 8 September 2026.
Release type: engineering experiment baseline / working prototype.
Source baseline: the commit titled `Experiment Complete 2026-09-08`, containing the reviewed implementation, tests and closure documentation. Origin is the existing private repository.
Routine production deployment readiness is not claimed.

## Outcome

The experiment produced a field-demonstrated seed-to-supported-neighbour diagnostic collection workflow and a documented Architect / Implementer / Reviewer cycle under human direction.

The closure working tree includes:

- Correct downstream Aruba-CX identity/profile selection.
- Recursive discovery enabled by default; `--no-recurse` selects flat collection.
- A configured target can seed discovery without an existing topology file.
- Sequential and parallel identity deduplication from PHASE-087.
- Canonical alias back-edges with retained alias/address evidence from PHASE-087A.
- Raw command capture, structured troubleshooting artefacts, progress, streaming updates, checkpoints and build provenance.

PHASE-090 corrects the README, supplies the experiment report and demonstration, records the baseline/publication review, and defers PHASE-088/089 to continuation. It changes no application code.

## Evidence and limitations

The PHASE-086 archive establishes collection on two physical switches before the two identity fixes, including one redundant alias collection. PHASE-087/087A are approved via regression and direct topology reproduction. No supplied post-fix live archive or newly built closure ZIP is claimed.

Current verification: 354 tests passed, one established profile-fallback warning; documented offline packaging and topology examples verified. On a working environment:

```powershell
$releaseTests = Join-Path 'build' ('release-tests-' + [guid]::NewGuid().ToString('N'))
& $demoPython -m pytest -q -o addopts= --basetemp $releaseTests
```

Set `$demoPython` using [DEMONSTRATION.md](DEMONSTRATION.md). Exact source fingerprint and environment details are in [EXPERIMENT-CLOSURE.md](EXPERIMENT-CLOSURE.md).

The repository contains historical exposure candidates, including credential-bearing configuration history. No public release clearance is implied. Existing ZIPs are historical artefacts and must not be relabelled as this release.

## Tag preparation

Recommended annotated tag: **`experiment-complete-2026-09`**.

After verifying the exact hash and source fingerprint of the user-authorised closure commit, use these notes as the annotation:

```text
git tag -a experiment-complete-2026-09 <verified-closure-commit> -F RELEASE_NOTES.md
```

Replace the placeholder with the verified hash of the closure commit. The earlier assessment HEAD (`33bfd97`) lacks the reviewed implementation. The user subsequently authorised committing the complete baseline and pushing to the existing private origin; no tag or release-asset upload is part of that request.

Archive the experiment repository after baseline capture. Continue selected Enhancement, Roadmap or Research work in a separate repository following [CONTINUATION-HANDOVER.md](CONTINUATION-HANDOVER.md).
