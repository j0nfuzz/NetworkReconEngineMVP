"""Shared pytest configuration and fixtures."""
from __future__ import annotations

import os

# Suppress git-based provenance capture by default to avoid subprocess crashes in CI/AV.
# Set the env var before importing app.provenance so its import-time initialisation disables capture.
os.environ["NRE_DISABLE_PROVENANCE"] = "1"

import app.provenance as provenance_module  # noqa: E402

provenance_module.set_provenance_capture_enabled(False)

import pytest  # noqa: E402

import app.orchestrator as orchestrator_module  # noqa: E402


class _NetworkBlockedSSHClient:
    """Network-boundary stub for identity probes in orchestrator tests.

    PHASE-084 extended identity probing to discovered neighbours lacking
    identity metadata. Orchestrator tests that do not stub
    app.orchestrator.DeviceSSHClient themselves would otherwise attempt
    real (TEST-NET) connections. probe() fails fast and deterministically;
    connect()/run_command() surface accidental real SSH use as test errors.
    Tests exercising probe logic patch DeviceSSHClient with their own fakes,
    which override this fixture.
    """

    def __init__(self, *args, **kwargs):
        pass

    def probe(self):
        return {"reachable": False, "error": "network access blocked in tests"}

    def connect(self):
        raise AssertionError("real SSH connect attempted in orchestrator test")

    def run_command(self, command, client=None):
        raise AssertionError("real SSH command attempted in orchestrator test")

    def close(self, connection):
        pass


@pytest.fixture(autouse=True)
def _block_real_identity_probe_network(monkeypatch):
    monkeypatch.setattr(orchestrator_module, "DeviceSSHClient", _NetworkBlockedSSHClient)
