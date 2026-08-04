# Wishlist.md
# Network Device Diagnostics - Vision / Roadmap

## Goal

Build a vendor-agnostic network diagnostics platform capable of:

- Connecting to a seed device via SSH.
- Detecting device vendor, platform and role automatically.
- Collecting standardised troubleshooting data.
- Discovering neighbouring infrastructure devices.
- Traversing network topology.
- Building a complete diagnostic inventory of an environment.
- Producing AI-ready troubleshooting bundles.
- Producing engineer-friendly health assessments.
- Supporting future autonomous diagnostic workflows.

The desired outcome is:

"Point the tool at one network device and receive a complete troubleshooting package for the discovered infrastructure."

---

## Existing Direction

Current architecture already broadly supports:

- SSH connectivity
- Vendor-specific command profiles
- Device collection
- Structured output
- Bundled diagnostic data

Existing samples indicate collection of:

Cisco:
- show version
- show inventory
- show interfaces
- show routes
- CPU
- memory
- ARP
- CDP neighbours
- logs

Juniper:
- version
- interfaces
- ARP
- routing
- LLDP
- logs
- system processes

Current structure is considered sound.

Do not replace.
Extend.

---

## Phase 1 - Vendor Detection

Automatically determine platform after login.

Examples:

- Cisco IOS
- Cisco IOS-XE
- Cisco NX-OS
- ArubaOS-CX
- Aruba ProCurve
- FortiGate
- Juniper JunOS
- Extreme
- HP Comware
- Unknown

Detection should occur immediately after authentication.

Output:

{
  vendor: "Cisco",
  platform: "IOS-XE",
  model: "C9300-48P"
}

Purpose:

Allows command selection without manual intervention.

---

## Phase 2 - Role Detection

Attempt to classify device role.

Possible roles:

- Access Switch
- Distribution Switch
- Core Switch
- Router
- Firewall
- Wireless Controller
- Access Point
- Server
- Unknown

Methods:

- Hostname analysis
- Model identification
- Routing table presence
- Firewall process detection
- LLDP/CDP characteristics

Purpose:

Role determines collection depth and relevant command sets.

---

## Phase 3 - Vendor Command Profiles

Maintain separate command collections per vendor and role.

Example:

Cisco Switch

- show version
- show inventory
- show interfaces status
- show interface counters errors
- show spanning-tree summary
- show mac address-table count
- show cdp neighbors detail
- show logging
- show processes cpu sorted
- show memory statistics

Cisco Router

- show version
- show ip route summary
- show interfaces
- show arp
- show logging
- show processes cpu sorted

FortiGate

- get system status
- get hardware nic
- get router info routing-table all
- get system performance status
- diagnose sys top-summary
- diagnose hardware deviceinfo nic
- show firewall policy
- execute log display

Aruba CX

- show version
- show system
- show interfaces brief
- show lldp neighbors-info detail
- show arp
- show vlan
- show logging
- show cpu
- show memory

Design principle:

Collect evidence that engineers would actually request during troubleshooting.

Avoid collecting unnecessary noise.

---

## Phase 4 - Device Discovery

After collection, inspect:

- CDP neighbours
- LLDP neighbours
- ARP tables
- Routing information
- Vendor topology data

Build topology graph.

Example:

FW01
├─ SW01
│  ├─ SW02
│  ├─ AP01
│  └─ AP02
└─ SW03

Store graph independently of diagnostics.

Discovery should occur before recursive collection.

Important:

Discovery phase learns topology.

It does not immediately connect everywhere.

---

## Phase 5 - Topology Graph

Implement graph-based network representation.

Example:

{
  "SW01": {
     "neighbours": [
        "SW02",
        "FW01"
     ]
  }
}

Requirements:

- Unique node tracking
- Edge tracking
- Vendor tracking
- IP tracking
- Device role tracking

Graph should support:

- Visualisation
- Search
- Traversal
- Future topology export

---

## Phase 6 - Traversal Engine

Do NOT use naive recursion.

Use graph traversal.

Maintain:

visited
pending
failed
successful

Example:

Visit SW01
 -> discover SW02
 -> discover FW01

Visit SW02
 -> discover SW03

Visit FW01
 -> discover ISP-RTR

Benefits:

- No loops
- Deterministic behaviour
- Easier recovery
- Scalable

Required protection:

Prevent:

SW01 -> SW02 -> SW01 -> SW02 forever

---

## Phase 7 - Recursive Neighbour Collection

Once a neighbour is identified:

1. Determine if supported.
2. Determine if reachable.
3. Attempt connection.
4. Collect baseline diagnostics.
5. Add discovered neighbours to queue.

Repeat until traversal complete.

Supported examples:

- Cisco
- Aruba
- FortiGate
- Juniper

Unsupported examples:

- Printers
- UPS devices
- Phones
- IoT devices
- Unknown systems

Unsupported devices should be recorded but skipped.

---

## Phase 8 - Credential Management

Support:

Global credentials:

default:
  username:
  password:

"<PASSWORD>"

FW01:
  username:
  password:

"<PASSWORD>"

- Minimal prompting
- Reusable sessions
- Multiple vendor support

Future:

- Encrypted credential store
- Secure vault support

---

## Phase 9 - Parallel Collection

Support concurrent SSH sessions.

Target architecture:

asyncio
asyncssh

Benefits:

- Faster collection
- Faster discovery

Control:

Maximum concurrent sessions.

Example:

MAX_CONCURRENT = 10

Avoid:

- AAA overload
- RADIUS overload
- TACACS overload
- Device stress

Concurrency should be configurable.

---

## Phase 10 - Checkpointing

Critical feature.

Persist state during execution.

Store:

- discovered
- visited
- pending
- successful
- failed

Example:

checkpoint.json

If run fails at device 273:

Resume at device 274.

Do NOT restart entire estate discovery.

This becomes extremely valuable in large environments.

---

## Phase 11 - Health Scoring

Implement rules-based diagnostic assessment.

Example:

Health Score: 78/100

Warnings:
- Memory utilisation high
- Interface errors detected
- Neighbour flapping observed

Critical:
- None

Rules should be deterministic.

No AI required.

Use:

- Regex
- Thresholds
- Pattern matching

Purpose:

Quick engineer triage.

---

## Phase 12 - Data Normalisation

Raw command output remains available.

Additionally produce:

summary.json

Example:

{
  "hostname": "SW01",
  "vendor": "Cisco",
  "model": "C9300",
  "version": "17.9.5",
  "uptime_days": 183,
  "cpu": 12,
  "memory": 48,
  "routes": 143,
  "arp_entries": 821,
  "interface_errors": [
      "Gi1/0/24"
  ]
}

Purpose:

Create consistent vendor-independent representation.

Allows future analytics.

---

## Phase 13 - AI Troubleshooting Bundle

Generate structured AI briefing.

Example:

# Network Diagnostic Summary

Device:
SW01

Vendor:
Cisco

Model:
C9300

Potential Issues:

- CRC errors on Gi1/0/24
- CPU spikes recorded
- LLDP neighbour instability

Attached Data:

- version
- logging
- interfaces
- routing

Requested Analysis:

1. Probable root causes
2. Immediate risks
3. Remediation actions
4. Escalation recommendations

Purpose:

Feed directly into LLM analysis.

Reduce token waste.

Improve analysis quality.

---

## Phase 14 - Topology-Aware Troubleshooting

Future intelligent mode.

Example:

AP12 reports offline.

Automatically collect:

AP12
SW02
SW01
FW01

Rather than:

Entire estate

Benefits:

- Faster diagnostics
- Smaller bundles
- Reduced collection time

Tool begins behaving like an engineer rather than a collector.

---

## Phase 15 - Future Vision

Ultimately evolve into:

Infrastructure Reconnaissance Engine

Capabilities:

- Discovery
- Topology mapping
- Health scoring
- Diagnostic collection
- AI packaging
- Intelligent scoping
- Fault-domain tracking
- Dependency analysis

Desired engineer experience:

Target one device.

Return:

- Topology map
- Device inventory
- Health assessment
- Key risks
- AI-ready diagnostic bundle
- Structured evidence package

In other words:

"Stop manually SSH'ing into fifty bloody devices."