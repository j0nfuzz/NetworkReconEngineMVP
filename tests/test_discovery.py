from __future__ import annotations

import pytest

from app.discovery import extract_neighbors


ARUBA_CX_LLDP_DETAIL = """\
LLDP Neighbor Information
=========================

Total Neighbor Entries          : 8
Total Neighbor Entries Deleted  : 1408
Total Neighbor Entries Dropped  : 0
Total Neighbor Entries Aged-Out : 1408

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
Neighbor TX Wake time          : 0 us
Neighbor RX Wake time          : 0 us
Neighbor Fallback time         : 0 us
Neighbor TX Echo time          : 0 us
Neighbor RX Echo time          : 0 us

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
"""


def test_extract_neighbors_arubacx_lldp_detail_finds_neighbors():
    neighbors = extract_neighbors("aruba", {"show lldp neighbor-info detail": ARUBA_CX_LLDP_DETAIL})
    assert len(neighbors) == 2
    by_name = {n["neighbor"]: n for n in neighbors}
    assert "NEIGHBOR-01" in by_name
    assert by_name["NEIGHBOR-01"] == {
        "neighbor": "NEIGHBOR-01",
        "ip": "192.0.2.10",
        "source": "show lldp neighbor-info detail",
    }
    assert by_name["00:11:22:33:44:55"] == {
        "neighbor": "00:11:22:33:44:55",
        "platform": "00:11:22:33:44:55",
        "source": "show lldp neighbor-info detail",
    }


def test_extract_neighbors_arubacx_lldp_detail_uses_chassis_id_when_no_system_name():
    detail = """\
--------------------------------------------------------------------------------
Port                           : 1/1/1
Neighbor System-Name           :
Neighbor Chassis-ID            : 00:11:22:33:44:55
Neighbor Management-Address    :
Neighbor Port-ID               : eth1
--------------------------------------------------------------------------------
"""
    neighbors = extract_neighbors("aruba", {"show lldp neighbor-info detail": detail})
    assert len(neighbors) == 1
    neighbor = neighbors[0]
    assert neighbor["neighbor"] == "00:11:22:33:44:55"
    assert "ip" not in neighbor
    assert neighbor.get("platform") == "00:11:22:33:44:55"


def test_extract_neighbors_arubacx_lldp_detail_uses_management_address_fallback():
    detail = """\
--------------------------------------------------------------------------------
Port                           : 1/1/1
Neighbor System-Name           :
Neighbor Chassis-ID            : 00:11:22:33:44:57
Neighbor Management-Address    : 192.0.2.20,2001:db8::20
Neighbor Port-ID               : eth1
--------------------------------------------------------------------------------
"""
    neighbors = extract_neighbors("aruba", {"show lldp neighbor-info detail": detail})
    assert len(neighbors) == 1
    assert neighbors[0]["neighbor"] == "192.0.2.20"
    assert neighbors[0]["ip"] == "192.0.2.20"


def test_extract_neighbors_generic_lldp_labels_still_parsed():
    output = """\
Chassis id: 00 00 5e 00 53 04
System Name: CORE-SW01

Chassis id: 10.0.0.5
System Name: EDGE-SW01
"""
    neighbors = extract_neighbors("cisco", {"show lldp neighbors": output})
    by_name = {n["neighbor"]: n for n in neighbors}
    assert "CORE-SW01" in by_name
    assert "EDGE-SW01" in by_name
    assert by_name["EDGE-SW01"]["ip"] == "10.0.0.5"
