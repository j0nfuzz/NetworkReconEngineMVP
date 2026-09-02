from __future__ import annotations

from copy import deepcopy

from app.troubleshooting import build_troubleshooting_bundle


def test_build_troubleshooting_bundle_complete():
    summary = {
        "hostname": "sw01.example",
        "vendor": "cisco",
        "model": "C9300-48P",
        "version": "17.09.04",
    }
    health = {
        "score": 85,
        "warnings": ["CPU utilisation high"],
        "critical": [],
    }
    raw_outputs = {
        "show version": "...",
        "show interfaces": "...",
    }
    result = build_troubleshooting_bundle(summary, health, raw_outputs)

    assert result["hostname"] == "sw01.example"
    assert result["vendor"] == "cisco"
    assert result["model"] == "C9300-48P"
    assert result["version"] == "17.09.04"
    assert result["health_score"] == 85
    assert result["warnings"] == ["CPU utilisation high"]
    assert result["critical"] == []
    assert result["evidence"] == ["show interfaces", "show version"]
    assert "sw01.example" in result["briefing"]
    assert "CPU utilisation high" in result["briefing"]
    assert "show version" in result["briefing"]
    assert "..." not in result["briefing"]


def test_build_troubleshooting_bundle_missing_data():
    result = build_troubleshooting_bundle({}, {}, {})
    assert result["hostname"] == "unknown"
    assert result["vendor"] == "unknown"
    assert result["model"] == "unknown"
    assert result["version"] == "unknown"
    assert result["health_score"] == 100
    assert result["warnings"] == []
    assert result["critical"] == []
    assert result["evidence"] == []
    assert "No warnings" in result["briefing"]


def test_build_troubleshooting_bundle_deterministic_shape():
    result = build_troubleshooting_bundle({}, {}, {})
    expected_keys = {
        "hostname",
        "vendor",
        "model",
        "version",
        "health_score",
        "warnings",
        "critical",
        "evidence",
        "failed_commands",
        "failed_command_details",
        "briefing",
    }
    assert set(result.keys()) == expected_keys
    assert result["evidence"] == sorted(result["evidence"])


def test_build_troubleshooting_bundle_evidence_is_referenced():
    raw_outputs = {"show version": "long output", "show arp": "more output"}
    result = build_troubleshooting_bundle({}, {}, raw_outputs)
    assert result["evidence"] == ["show arp", "show version"]
    for source in result["evidence"]:
        assert source in result["briefing"]
    assert "long output" not in result["briefing"]
    assert "more output" not in result["briefing"]


def test_build_troubleshooting_bundle_does_not_mutate_inputs():
    summary = {"hostname": "sw01"}
    health = {"score": 90, "warnings": [], "critical": []}
    raw_outputs = {"show version": "x"}
    original_summary = deepcopy(summary)
    original_health = deepcopy(health)
    original_raw = deepcopy(raw_outputs)

    build_troubleshooting_bundle(summary, health, raw_outputs)

    assert summary == original_summary
    assert health == original_health
    assert raw_outputs == original_raw
