import json

from app.checkpoint import CheckpointError, load_checkpoint, save_checkpoint, state_to_checkpoint
from app.orchestrator import run_recursive_collection
from app.models import Device, DeviceBundle


def _make_bundle(name, vendor, status, neighbors):
    return DeviceBundle(
        device_name=name,
        device_vendor=vendor,
        timestamp="2026-08-05T00:00:00Z",
        summary={
            "status": status,
            "discovered_neighbors": neighbors,
        },
    )


def test_save_and_load_checkpoint_roundtrip(tmp_path):
    path = tmp_path / "checkpoint.json"
    state = {
        "visited": {"SW01", "SW02"},
        "pending": ["SW03"],
        "successful": ["SW01"],
        "failed": ["SW02"],
        "unsupported": ["PR01"],
    }
    save_checkpoint(path, state)
    loaded = load_checkpoint(path)

    assert loaded["visited"] == {"SW01", "SW02"}
    assert loaded["pending"] == ["SW03"]
    assert loaded["successful"] == ["SW01"]
    assert loaded["failed"] == ["SW02"]
    assert loaded["unsupported"] == ["PR01"]


def test_load_missing_checkpoint_returns_none(tmp_path):
    assert load_checkpoint(tmp_path / "does_not_exist.json") is None


def test_load_corrupt_checkpoint_raises(tmp_path):
    path = tmp_path / "bad.json"
    path.write_text("not json", encoding="utf-8")
    try:
        load_checkpoint(path)
    except CheckpointError as exc:
        assert "not valid JSON" in str(exc)
    else:
        raise AssertionError("Expected CheckpointError")


def test_checkpoint_content_is_plain_json(tmp_path):
    path = tmp_path / "checkpoint.json"
    save_checkpoint(path, {
        "visited": {"A"},
        "pending": ["B"],
        "successful": ["A"],
        "failed": [],
        "unsupported": [],
    })
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert payload["visited"] == ["A"]
    assert payload["pending"] == ["B"]


def test_state_to_checkpoint_sorted_pending():
    state = state_to_checkpoint(
        visited={"B", "A"},
        queued={"C", "B"},
        successful=["A"],
        failed=["D"],
        unsupported=["E"],
    )
    assert state["pending"] == ["B", "C"]


def test_on_collected_callback_receives_state(monkeypatch, tmp_path):
    seed = Device(name="SW01", hostname="10.0.0.1", vendor="cisco")
    collector = {
        "SW01": _make_bundle("SW01", "cisco", "collected", []),
    }
    monkeypatch.setattr(
        "app.orchestrator.execute_device_collection",
        lambda d: collector[d.name],
    )

    captured = []
    def callback(state):
        captured.append(state)
        save_checkpoint(tmp_path / "cp.json", state)

    run_recursive_collection(seed, on_collected=callback)
    assert len(captured) == 1
    assert "visited" in captured[0]
    assert "pending" in captured[0]
    assert load_checkpoint(tmp_path / "cp.json") is not None


def test_resume_from_checkpoint_skips_visited_and_collects_pending(monkeypatch, tmp_path):
    responses = {
        "SW01": _make_bundle(
            "SW01",
            "cisco",
            "collected",
            [{"neighbor": "SW02", "ip": "10.0.0.2", "platform": "cisco WS-C2960-24TC-L"}],
        ),
        "SW02": _make_bundle("SW02", "cisco", "collected", []),
    }
    calls = []
    def collecting(d):
        calls.append(d.name)
        return responses[d.name]

    monkeypatch.setattr("app.orchestrator.execute_device_collection", collecting)

    checkpoint = {
        "visited": {"SW01"},
        "pending": ["SW02"],
        "successful": ["SW01"],
        "failed": [],
        "unsupported": [],
    }
    save_checkpoint(tmp_path / "resume.json", checkpoint)
    loaded = load_checkpoint(tmp_path / "resume.json")

    resumed = run_recursive_collection(
        Device(name="SW01", hostname="10.0.0.1", vendor="cisco"),
        resume_state=loaded,
    )
    assert calls == ["SW02"]
    assert resumed["successful"] == ["SW01", "SW02"]
    assert resumed["failed"] == []


def test_checkpoint_callback_includes_newly_discovered_neighbors(monkeypatch, tmp_path):
    responses = {
        "SW01": _make_bundle(
            "SW01",
            "cisco",
            "collected",
            [{"neighbor": "SW02", "ip": "10.0.0.2", "platform": "cisco WS-C2960-24TC-L"}],
        ),
        "SW02": _make_bundle("SW02", "cisco", "collected", []),
    }
    monkeypatch.setattr(
        "app.orchestrator.execute_device_collection",
        lambda d: responses[d.name],
    )

    captured = []
    def callback(state):
        captured.append(state)
        save_checkpoint(tmp_path / "cp.json", state)

    run_recursive_collection(
        Device(name="SW01", hostname="10.0.0.1", vendor="cisco"),
        on_collected=callback,
    )
    assert len(captured) == 2
    assert captured[0]["pending"] == ["SW02"]
    assert captured[1]["pending"] == []


def test_failed_collection_is_checkpointed(monkeypatch, tmp_path):
    seed = Device(name="SW01", hostname="10.0.0.1", vendor="cisco")
    monkeypatch.setattr(
        "app.orchestrator.execute_device_collection",
        lambda d: _make_bundle(d.name, d.vendor, "unreachable", []),
    )

    captured = []
    def callback(state):
        captured.append(state)
        save_checkpoint(tmp_path / "cp.json", state)

    result = run_recursive_collection(seed, on_collected=callback)
    assert result["failed"] == ["SW01"]
    assert len(captured) == 1
    assert captured[0]["failed"] == ["SW01"]

    loaded = load_checkpoint(tmp_path / "cp.json")
    assert loaded["failed"] == ["SW01"]


def test_resume_preserves_previously_failed_devices(monkeypatch, tmp_path):
    responses = {
        "SW02": _make_bundle("SW02", "cisco", "collected", []),
    }
    calls = []
    def collecting(d):
        calls.append(d.name)
        return responses[d.name]

    monkeypatch.setattr("app.orchestrator.execute_device_collection", collecting)

    checkpoint = {
        "visited": {"SW01"},
        "pending": ["SW02"],
        "successful": [],
        "failed": ["SW01"],
        "unsupported": [],
    }
    save_checkpoint(tmp_path / "resume.json", checkpoint)
    loaded = load_checkpoint(tmp_path / "resume.json")

    resumed = run_recursive_collection(
        Device(name="SW01", hostname="10.0.0.1", vendor="cisco"),
        resume_state=loaded,
    )
    assert calls == ["SW02"]
    assert resumed["successful"] == ["SW02"]
    assert resumed["failed"] == ["SW01"]
