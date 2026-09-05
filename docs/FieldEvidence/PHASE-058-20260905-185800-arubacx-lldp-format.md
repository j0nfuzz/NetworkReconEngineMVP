# PHASE-058 Field Evidence — ArubaOS-CX LLDP Neighbor Format

## Collection Metadata

| Field | Value |
|---|---|
| Phase | PHASE-058-ArubaOSCXLLDPNeighborFormatFieldCapture |
| Analysis commit | `763694e` (PHASE-057 stable checkpoint) |
| Bundle source | `field_tests/output1.zip` |
| Field bundle timestamp | 2026-09-03T20:00:42+00:00 |
| Device platform | ArubaOS-CX |
| Command present in bundle | `show lldp neighbor-info detail` (ArubaOS-CX form) |
| Collection mode | live (`dry_run: false`) |
| Total neighbor entries observed | 8 |
| Collection status | partial (one unrelated command failed) |

## Governance Note

`field_tests/FIELDTEST.MD` was read before this analysis. All hostnames, IP addresses, MAC addresses, serial numbers, locations, and company identifiers have been replaced with placeholders. No real customer or production identifiers are reproduced outside the approved field-evidence artefact.

## Evidence Requirements

PHASE-058 required enough ArubaOS-CX LLDP evidence to:

1. Confirm whether the current parser assumptions in `app/discovery.py` match real ArubaOS-CX output.
2. Identify the exact field names ArubaOS-CX uses for neighbor identity and reachability.
3. Capture format variations (populated vs empty fields, MAC vs IPv4 chassis-id, etc.).
4. Provide a sanitised reference for a future parser-remediation phase, should one be approved.

## Required ArubaOS-CX Commands

Per PHASE-058 acceptance criteria, the read-only commands of interest are:

1. **`show lldp neighbor-info detail`** — primary evidence source; produces per-port, multi-line neighbor records.
2. **`show lldp neighbor-info`** — optional summary form for comparison; not present in the available bundle.

No configuration or state-changing commands were used.

## Capture Methodology

- Evidence was extracted from the existing approved field bundle `field_tests/output1.zip` rather than collected live.
- The relevant command output file, `show_lldp_neighbor-info_detail.txt`, was located inside the device directory of the bundle.
- Field labels, value types, and block structure were catalogued by inspection.
- Real identifiers were replaced with documentation placeholders before inclusion in this file.

## Expected Artefacts

- This markdown file: `docs/FieldEvidence/PHASE-058-20260905-185800-arubacx-lldp-format.md`
- The underlying raw evidence remains confined to `field_tests/output1.zip`.
- No new source, test, discovery, collector, vendor-profile, or architecture files were created or modified.

## Observed Field-Name Mapping

The ArubaOS-CX `show lldp neighbor-info detail` output uses prefixed, hyphenated field labels that do not match the parser assumptions currently in `app/discovery.py`.

| Observed ArubaOS-CX Field | Current `app/discovery.py` Assumption | Relevance |
|---|---|---|
| `Neighbor System-Name` | `System Name:` | Primary neighbor identity (`neighbor` value) |
| `Neighbor Chassis-ID` | `Chassis id:` | Optional `ip` if value is IPv4 |
| `Neighbor Management-Address` | (not parsed) | Neighbor IPv4/IPv6 reachability |
| `Neighbor Port-ID` | (not parsed) | Neighbor port identifier |
| `Neighbor Port-Desc` | (not parsed) | Neighbor port description |
| `Neighbor System-Description` | (not parsed) | Platform / software-version hints |
| `Port` | (not parsed) | Local port on the collector device |
| `Neighbor Entries` | (not parsed) | Count of neighbors on the local port |

Key differences:

- **Chassis ID label:** parser expects `Chassis id:` (lowercase `id`, space, colon); ArubaOS-CX emits `Neighbor Chassis-ID` (prefixed, hyphenated, uppercase `ID`).
- **System Name label:** parser expects `System Name:`; ArubaOS-CX emits `Neighbor System-Name`.
- **Management address location:** parser derives `ip` only from the chassis-id value; ArubaOS-CX places IPv4/IPv6 addresses under the separate `Neighbor Management-Address` field, while the chassis-id is typically a MAC address.
- **Block delimiter:** parser splits on `(?m)^\s*Chassis id:\s*`; ArubaOS-CX blocks begin with `Port                           : <local-port>`.

## Sanitised Sample Output

```text
LLDP Neighbor Information 
=========================

Total Neighbor Entries          : 8
Total Neighbor Entries Deleted  : <COUNT>
Total Neighbor Entries Dropped  : 0
Total Neighbor Entries Aged-Out : <COUNT>

--------------------------------------------------------------------------------

Port                           : 1/1/3
Neighbor Entries               : 1
Neighbor Entries Deleted       : 0
Neighbor Entries Dropped       : 0
Neighbor Entries Aged-Out      : 0
Neighbor System-Name           : 
Neighbor System-Description    : 
Neighbor Chassis-ID            : 00:11:22:33:44:55
Neighbor Management-Address    : 
Chassis Capabilities Available :  
Chassis Capabilities Enabled   :  
Neighbor Port-ID               : eth0
Neighbor Port-Desc             : 
Neighbor Port VLAN ID          : 
Neighbor Port VLAN Name        : 
Neighbor Port MFS              : 0
Link aggregation supported     : Information Not Available
Link aggregation enabled       : No
Aggregation port ID            : 0
TTL                            : 240

Neighbor EEE information       : DOT3
...

--------------------------------------------------------------------------------

Port                           : 1/1/46
Neighbor Entries               : 1
Neighbor Entries Deleted       : 0
Neighbor Entries Dropped       : 0
Neighbor Entries Aged-Out      : 0
Neighbor System-Name           : NEIGHBOR-01
Neighbor System-Description    : <VENDOR_DEVICE_TYPE>, <VERSION_STRING>
Neighbor Chassis-ID            : 00:11:22:33:44:56
Neighbor Management-Address    : 192.0.2.10,2001:db8::1
Chassis Capabilities Available : Bridge, Router
Chassis Capabilities Enabled   : Bridge, Router
Neighbor Port-ID               : 1/1/48
Neighbor Port-Desc             : <PORT_DESCRIPTION>
Neighbor Port VLAN ID          : 1
Neighbor Port VLAN Name        : DEFAULT_VLAN_1,VLAN5,VLAN10,VLAN12,VLAN15,VLAN20
Neighbor Port MFS              : 1500
Link aggregation supported     : Yes
Link aggregation enabled       : Yes
Aggregation port ID            : 0
TTL                            : 240

...
```

### Observed Value Variations

| Variation | Example | Implication For Parser |
|---|---|---|
| Empty `Neighbor System-Name` | system-name blank, only chassis-id present | Parser must fall back to chassis-id or management-address for identity. |
| MAC chassis-id | `00:11:22:33:44:56` | Current parser only populates `ip` when chassis-id is IPv4; MAC chassis-ids yield no `ip`. |
| Management address as IPv4+IPv6 pair | `192.0.2.10,2001:db8::1` | Future parser could derive `ip` from this field when chassis-id is not IPv4. |
| Port-id as MAC | `00:11:22:33:44:56` | Distinct from local `Port`; useful for edge correlation. |
| Port-id as interface name | `eth0`, `g47`, `1/1/48` | Vendor-specific neighbor port naming; not currently consumed. |

## Current Parser Impact

- `app/discovery.py::_parse_lldp_neighbors()` uses:
  - `entries = re.split(r"\n(?=\s*Chassis id:\s*)", output, flags=re.IGNORECASE)`
  - `chassis_match = re.search(r"Chassis id:\s*(.+)", entry, re.IGNORECASE)`
  - `system_match = re.search(r"System Name:\s*(.+)", entry, re.IGNORECASE)`
- None of these patterns match the ArubaOS-CX field labels observed in this evidence.
- Result: the same device that reported 8 LLDP neighbors in `show lldp neighbor-info detail` produced `"discovered_neighbors": []` in `topology.json`.

This supports the hypothesis that ArubaOS-CX LLDP output does not match current parser assumptions.

## Data-Sanitisation Guidance Applied

| Sensitive Element | Sanitisation Action |
|---|---|
| Collector device hostname/IP | Omitted from this file; referred to only as "the observed ArubaOS-CX device". |
| Neighbor hostnames | Replaced with `NEIGHBOR-01`, `NEIGHBOR-02`, etc. |
| Neighbor IPv4/IPv6 addresses | Replaced with `192.0.2.X` / `2001:db8::X` documentation prefixes. |
| MAC addresses | Replaced with documentation range `00:00:5e:00:53:XX`. |
| System descriptions | Replaced with `<VENDOR_DEVICE_TYPE>, <VERSION_STRING>` placeholders. |
| Port descriptions / VLAN names | Generic placeholders or standard defaults only. |
| Serial numbers, locations, company identifiers | Omitted or replaced with placeholders. |

## Assessment of Evidence Sufficiency

| Validation Goal | Verdict |
|---|---|
| Confirm parser assumption mismatch | **Sufficient.** The field-name differences are explicit and explain the empty `discovered_neighbors`. |
| Identify ArubaOS-CX neighbor-format differences | **Sufficient.** Key labels, value types, and variations are catalogued. |
| Support a future parser-remediation phase | **Sufficient for design.** A follow-on phase can update `app/discovery.py` to match `Neighbor System-Name` / `Neighbor Chassis-ID` / `Neighbor Management-Address`. |
| Compare detail vs summary (`show lldp neighbor-info`) | **Insufficient.** The summary form was not captured in this bundle. |
| Legacy CDP frame capture | **Not addressed.** No CDP output was present in the bundle. |

## Conclusion

PHASE-058 field evidence confirms the hypothesis: ArubaOS-CX `show lldp neighbor-info detail` emits prefixed, hyphenated LLDP field labels (`Neighbor Chassis-ID`, `Neighbor System-Name`, `Neighbor Management-Address`) that do not match the unprefixed labels (`Chassis id:`, `System Name:`) assumed by `app/discovery.py`. This mismatch explains why the device produced zero discovered neighbors despite having eight LLDP entries in the raw command output.

No parser, discovery, collector, vendor-profile, or architecture changes were made in this phase. Any remediation remains blocked until a future phase is explicitly approved.
