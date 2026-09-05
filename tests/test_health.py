from __future__ import annotations

from app.health import score_device_health


def test_score_device_healthy():
    summary = {
        "hostname": "sw01",
        "cpu": 45.0,
        "memory": 50.0,
        "interface_errors": [],
        "uptime_days": 183,
    }
    result = score_device_health(summary)
    assert result["score"] == 100
    assert result["warnings"] == []
    assert result["critical"] == []


def test_score_device_high_cpu():
    summary = {"cpu": 85.0, "memory": 50.0, "interface_errors": [], "uptime_days": 10}
    result = score_device_health(summary)
    assert result["score"] == 85
    assert "CPU utilisation high" in result["warnings"]


def test_score_device_high_memory():
    summary = {"cpu": 45.0, "memory": 90.0, "interface_errors": [], "uptime_days": 10}
    result = score_device_health(summary)
    assert result["score"] == 85
    assert "Memory utilisation high" in result["warnings"]


def test_score_device_interface_errors():
    summary = {"cpu": 45.0, "memory": 50.0, "interface_errors": ["Gi1/0/24"], "uptime_days": 10}
    result = score_device_health(summary)
    assert result["score"] == 90
    assert any("Gi1/0/24" in warning for warning in result["warnings"])


def test_score_device_multiple_issues():
    summary = {"cpu": 95.0, "memory": 95.0, "interface_errors": ["Gi1/0/1"], "uptime_days": None}
    result = score_device_health(summary)
    assert result["score"] == 60
    assert len(result["warnings"]) == 3
    assert result["critical"] == []


def test_score_device_missing_data():
    summary = {}
    result = score_device_health(summary)
    assert result["score"] == 100
    assert result["warnings"] == []
    assert result["critical"] == []


def test_score_device_explicit_uptime_none_is_no_evidence():
    summary = {"uptime_days": None}
    result = score_device_health(summary)
    assert result["score"] == 100
    assert result["warnings"] == []
    assert result["critical"] == []


def test_score_device_output_shape():
    result = score_device_health({})
    assert set(result.keys()) == {"score", "warnings", "critical"}
    assert isinstance(result["score"], int)
    assert isinstance(result["warnings"], list)
    assert isinstance(result["critical"], list)


def test_score_device_partial_status_reduces_score():
    summary = {
        "cpu": 45.0,
        "memory": 50.0,
        "interface_errors": [],
        "status": "partial",
        "failed_commands": ["show cdp neighbors detail"],
    }
    result = score_device_health(summary)
    assert result["score"] == 85
    assert "Collection incomplete" in result["warnings"][0]


def test_score_device_failed_commands_reduces_score():
    summary = {
        "cpu": 45.0,
        "memory": 50.0,
        "interface_errors": [],
        "failed_commands": ["show lldp neighbors"],
    }
    result = score_device_health(summary)
    assert result["score"] == 85
    assert any("Collection incomplete" in warning for warning in result["warnings"])


def test_score_device_partial_with_other_issues_stacks_penalties():
    summary = {
        "cpu": 85.0,
        "memory": 50.0,
        "interface_errors": ["Gi1/0/24"],
        "status": "partial",
        "failed_commands": ["show cdp neighbors detail"],
    }
    result = score_device_health(summary)
    assert result["score"] == 60
    assert any("Collection incomplete" in warning for warning in result["warnings"])
    assert any("CPU utilisation high" in warning for warning in result["warnings"])


def test_score_device_empty_failed_commands_list_unchanged():
    summary = {
        "cpu": 45.0,
        "memory": 50.0,
        "interface_errors": [],
        "status": "collected",
        "failed_commands": [],
    }
    result = score_device_health(summary)
    assert result["score"] == 100
    assert result["warnings"] == []
