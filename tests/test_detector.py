from __future__ import annotations

from app.detector import classify_role, detect_vendor_from_show_version, identify_device
from app.models import DeviceIdentity, DeviceRole


def test_identify_device_cisco_ios_xe():
    output = "Cisco IOS-XE Software, Version 17.09.04\nModel Number: C9300-48P"
    identity = identify_device(output)
    assert identity.vendor == "cisco"
    assert identity.platform == "cisco ios-xe"
    assert identity.model == "c9300-48p"
    assert identity.confidence == 0.7


def test_identify_device_aruba_cx():
    output = "ArubaOS-CX (MODEL: 6300M) Version 10.13.1000"
    identity = identify_device(output)
    assert identity.vendor == "aruba"
    assert identity.platform == "arubaos-cx"
    assert identity.model == "6300m"
    assert identity.confidence == 0.6


def test_identify_device_juniper_junos():
    output = "Juniper Networks, Inc.\nModel: srx3400\nJUNOS Software Release [18.4R3-S2]"
    identity = identify_device(output)
    assert identity.vendor == "juniper"
    assert identity.platform == "junos"
    assert identity.model == "srx3400"
    assert identity.confidence == 0.6


def test_identify_device_arista_eos():
    output = "Arista EOS version 4.28.0F\nDCS-7150S-64-CL"
    identity = identify_device(output)
    assert identity.vendor == "arista"
    assert identity.platform == "arista eos"
    assert identity.model == "dcs-7150s-64-cl"
    assert identity.confidence == 0.5


def test_identify_device_unknown():
    identity = identify_device("some random banner text")
    assert identity.vendor == "generic"
    assert identity.platform == "unknown"
    assert identity.model == "unknown"
    assert identity.confidence == 0.0


def test_identify_device_empty():
    identity = identify_device("")
    assert identity == DeviceIdentity()


def test_detect_vendor_from_show_version_backwards_compatible():
    assert detect_vendor_from_show_version("Cisco IOS XE Software, Version 17.09.04") == "cisco"
    assert detect_vendor_from_show_version("ArubaOS-CX") == "aruba"
    assert detect_vendor_from_show_version("") is None


def test_classify_role_switch_from_hostname():
    identity = DeviceIdentity(vendor="cisco", platform="cisco ios-xe", model="c9300-48p")
    role = classify_role(identity, "acc-sw-01")
    assert role.role == "switch"
    assert role.confidence == 0.5


def test_classify_role_router_from_hostname():
    identity = DeviceIdentity(vendor="cisco", platform="cisco ios", model="isr4331")
    role = classify_role(identity, "wan-rtr-01")
    assert role.role == "router"
    assert role.confidence == 0.6


def test_classify_role_firewall_from_hostname():
    identity = DeviceIdentity(vendor="juniper", platform="junos", model="srx3400")
    role = classify_role(identity, "dc-fw-01")
    assert role.role == "firewall"
    assert role.confidence == 0.6


def test_classify_role_unknown():
    identity = DeviceIdentity()
    role = classify_role(identity, "some-device")
    assert role.role == "unknown"
    assert role.confidence == 0.0


def test_classify_role_switch_from_model():
    identity = DeviceIdentity(vendor="arista", platform="arista eos", model="dcs-7150s-64-cl")
    role = classify_role(identity, "spine-01")
    assert role.role == "switch"
    assert role.confidence == 0.5
