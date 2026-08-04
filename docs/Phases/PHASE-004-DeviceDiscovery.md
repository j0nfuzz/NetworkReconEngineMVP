PHASE:
Device Discovery (PoC)

FILES:
- app/discovery.py
- app/collector.py
- tests/test_cli.py

ACCEPTANCE CRITERIA:
- New app/discovery.py exposes extract_neighbors(vendor, raw_outputs) -> List[Dict[str, str]]
- Parses existing "show cdp neighbors detail" (cisco) and "show lldp neighbors detail" (juniper/arista/aruba) raw output already collected by PHASE-003 profiles
- Each discovered neighbour returns at minimum {"neighbor": <name>, "source": <command>}; ip included when parseable
- Returns an empty list when no neighbour-discovery command output is present or nothing parses (no exceptions)
- collector.py calls extract_neighbors() after collection and stores the result in bundle.summary["discovered_neighbors"]
- Dry-run collection does not error and yields an empty discovered_neighbors list (placeholder text is not real neighbour data)
- Tests cover: cisco CDP parsing with sample output, no-match fallback to empty list, dry-run summary field present and empty
- No regressions

CONSTRAINTS:
- No new SSH commands (parse only existing collected raw_outputs)
- No topology graph, storage, or traversal logic (deferred to Wishlist Phase 5/6)
- No recursive connection to discovered neighbours (deferred to Wishlist Phase 7)
- Parsing is regex/text based only; no new dependencies
- Maintain backwards compatibility with existing summary fields

KNOWN RISKS:
- CDP/LLDP output formatting varies across vendor software versions; regex parsing may miss some neighbours
- Aruba/Arista/Juniper LLDP parsing is best-effort and may need refinement once real device samples are available

OUTSTANDING RISKS:
- Identity/role confidence scoring remains unvalidated against real devices (carried from PHASE-001/002/003)

OPEN QUESTIONS:
- None.
