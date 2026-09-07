PHASE:
PHASE-087-DeviceIdentityDeduplicationByHostname

FILES:
- app/orchestrator.py
- app/parallel_collector.py

ACCEPTANCE CRITERIA:
- Before enqueueing a classification-derived neighbour, check whether any already-visited device's resolved hostname/management-address matches the neighbour's resolved IP/hostname; if so, treat it as the same physical device (do not re-collect; record it in topology as an alias/back-edge to the existing node) instead of queueing a new collection under the LLDP-reported name.
- Regression test proves a neighbour whose IP matches an already-visited device's hostname is not re-collected.
- Regression test proves genuinely distinct devices (different resolved addresses) are unaffected.
- topology.json continues to record the LLDP-observed edge/link even when the neighbour is recognised as an alias, so the physical connection (e.g. "LAG 2 to `<LOCATION>`") is not lost from the evidence.

CONSTRAINTS:
- No changes to classification, discovery/LLDP parsing, queueing of genuinely-new devices, or the PHASE-084 identity-probe gate.
- No changes to credential handling, SSH/transport, or checkpoint schema beyond what is strictly needed to record the alias relationship.
- Name-based dedup (existing behaviour) must remain the fallback when no resolved address is available.

KNOWN RISKS:
- Devices with multiple interfaces/management addresses could still evade this check if the LLDP-reported address differs from the address used to reach the device originally (e.g. management VLAN vs data VLAN address) — accept as a known limitation unless evidence shows otherwise.

OUTSTANDING RISKS:
- SW3-class real third-hop devices remain unproven in any bundle to date; this phase does not address that (no such device exists in current field evidence).

OPEN QUESTIONS:
- Whether alias detection should also apply across the parallel/scoped collection path (app/parallel_collector.py) or is sufficient on the sequential path alone; field evidence to date (FT070920261340) only exercises the sequential path.
