from __future__ import annotations

from app.models import DeviceBundle
from app.normalization import _find_cisco_interface_errors, build_device_summary


def _make_bundle(raw_outputs=None, summary=None, device_vendor="cisco") -> DeviceBundle:
    return DeviceBundle(
        device_name="SW01",
        device_vendor=device_vendor,
        timestamp="2026-08-04T00:00:00Z",
        summary=summary or {"hostname": "sw01.example", "vendor": device_vendor},
        raw_outputs=raw_outputs or {},
        failed_commands=[],
    )


def test_build_device_summary_full_cisco_output():
    raw = {
        "show version": """
Cisco IOS XE Software, Version 17.09.04
Model Number: C9300-48P
uptime is 2 years, 18 weeks, 4 days, 5 hours, 30 minutes
""",
        "show processes cpu sorted": "CPU utilization for five seconds: 12%/0%; one minute: 10%; five minutes: 11%",
        "show memory statistics": """Processor Pool Total: 100000  Used: 48000  Free: 52000
I/O Pool Total: 20000  Used: 1000  Free: 19000""",
        "show ip route summary": "IP routing table contains 143 routes",
        "show arp": """Protocol  Address          Age (min)  Hardware Addr   Type   Interface
Internet  10.0.0.1                -   abcd.1234.5678  ARPA   Vlan10
Internet  10.0.0.2              123   abcd.1234.5679  ARPA   Vlan10
""",
        "show interfaces": """GigabitEthernet1/0/24 is up
    12345 input errors, 678 CRC
GigabitEthernet1/0/1 is up
    0 input errors, 0 CRC""",
    }
    bundle = _make_bundle(raw_outputs=raw)
    result = build_device_summary(bundle)
    assert result["hostname"] == "sw01.example"
    assert result["vendor"] == "cisco"
    assert result["model"] == "C9300-48P"
    assert result["version"] == "17.09.04"
    assert result["uptime_days"] == 860  # 2*366 + 18*7 + 4
    assert result["cpu"] == 12.0
    assert result["memory"] == 48.0
    assert result["routes"] == 143
    assert result["arp_entries"] == 2
    assert "GigabitEthernet1/0/24" in result["interface_errors"]
    assert "GigabitEthernet1/0/1" not in result["interface_errors"]


def test_build_device_summary_missing_values_use_defaults():
    bundle = _make_bundle(raw_outputs={}, summary={"hostname": "sw02.example", "vendor": "cisco"})
    result = build_device_summary(bundle)
    assert result["hostname"] == "sw02.example"
    assert result["vendor"] == "cisco"
    assert result["model"] == "unknown"
    assert result["version"] == "unknown"
    assert result["uptime_days"] is None
    assert result["cpu"] is None
    assert result["memory"] is None
    assert result["routes"] is None
    assert result["arp_entries"] is None
    assert result["interface_errors"] == []


def test_build_device_summary_deterministic_shape():
    bundle = _make_bundle()
    result = build_device_summary(bundle)
    expected_keys = {
        "hostname",
        "vendor",
        "model",
        "version",
        "uptime_days",
        "cpu",
        "memory",
        "routes",
        "arp_entries",
        "interface_errors",
        "failed_commands",
        "failed_command_details",
        "recovered_commands",
    }
    assert set(result.keys()) == expected_keys


def test_build_device_summary_unknown_vendor_defaults():
    raw = {"show version": "Some other vendor"}
    bundle = _make_bundle(raw_outputs=raw, device_vendor="unknown")
    result = build_device_summary(bundle)
    assert result["vendor"] == "unknown"
    assert result["version"] == "unknown"
    assert result["model"] == "unknown"
    assert result["cpu"] is None
    assert result["memory"] is None


def test_build_device_summary_does_not_mutate_bundle():
    bundle = _make_bundle(raw_outputs={"show version": "Cisco IOS XE Software, Version 17.09.04"})
    original = dict(bundle.raw_outputs)
    build_device_summary(bundle)
    assert bundle.raw_outputs == original
    assert bundle.summary["vendor"] == "cisco"


def test_find_cisco_interface_errors_detects_nonzero_crc_after_zero_input_errors():
    output = """GigabitEthernet1/0/1 is up
    0 input errors, 678 CRC"""
    assert _find_cisco_interface_errors(output) == ["GigabitEthernet1/0/1"]


def test_find_cisco_interface_errors_evaluates_multiple_counters():
    output = """GigabitEthernet1/0/1 is up
    0 input errors, 0 output errors, 0 CRC
GigabitEthernet1/0/2 is up
    0 input errors, 5 output errors, 0 CRC
GigabitEthernet1/0/3 is up
    12 input errors, 0 CRC"""
    result = _find_cisco_interface_errors(output)
    assert "GigabitEthernet1/0/1" not in result
    assert "GigabitEthernet1/0/2" in result
    assert "GigabitEthernet1/0/3" in result
