from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional


class CheckpointError(Exception):
    """Raised when checkpoint loading fails."""


def save_checkpoint(path: str | Path, state: Dict[str, Any]) -> None:
    """Persist recursive-collection state to JSON."""
    payload = {
        "visited": list(state.get("visited", set())),
        "pending": list(state.get("pending", [])),
        "successful": list(state.get("successful", [])),
        "failed": list(state.get("failed", [])),
        "unsupported": list(state.get("unsupported", [])),
    }
    Path(path).write_text(json.dumps(payload, indent=2), encoding="utf-8")


def load_checkpoint(path: str | Path) -> Optional[Dict[str, Any]]:
    """Load recursive-collection state from JSON, or None if the file is missing."""
    path_obj = Path(path)
    if not path_obj.exists():
        return None

    try:
        payload = json.loads(path_obj.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise CheckpointError(f"Checkpoint file is not valid JSON: {path}") from exc

    return {
        "visited": set(payload.get("visited", [])),
        "pending": list(payload.get("pending", [])),
        "successful": list(payload.get("successful", [])),
        "failed": list(payload.get("failed", [])),
        "unsupported": list(payload.get("unsupported", [])),
    }


def state_to_checkpoint(
    *,
    visited: set[str],
    queued: set[str],
    successful: List[str],
    failed: List[str],
    unsupported: List[str],
) -> Dict[str, Any]:
    """Build a checkpoint-ready state dict from orchestrator internals."""
    return {
        "visited": visited,
        "pending": sorted(queued),
        "successful": successful,
        "failed": failed,
        "unsupported": unsupported,
    }
