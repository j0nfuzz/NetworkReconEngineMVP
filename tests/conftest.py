"""Shared pytest configuration and fixtures."""
from __future__ import annotations

import os

# Suppress git-based provenance capture by default to avoid subprocess crashes in CI/AV.
# Set the env var before importing app.provenance so its import-time initialisation disables capture.
os.environ["NRE_DISABLE_PROVENANCE"] = "1"

import app.provenance as provenance_module  # noqa: E402

provenance_module.set_provenance_capture_enabled(False)
