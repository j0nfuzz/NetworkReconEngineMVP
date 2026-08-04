from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class Device:
    name: str
    hostname: str
    vendor: str
    port: int = 22
    username: str = ""
    password: str = ""
    enable_password: Optional[str] = None
    timeout: int = 15
    host_key_policy: str = "auto"
    known_hosts: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Device":
        return cls(
            name=data.get("name", "unknown"),
            hostname=data.get("hostname", ""),
            vendor=data.get("vendor", "unknown").lower(),
            port=int(data.get("port", 22)),
            username=data.get("username", ""),
            password=data.get("password", ""),
            enable_password=data.get("enable_password"),
            timeout=int(data.get("timeout", 15)),
            host_key_policy=data.get("host_key_policy", "auto"),
            known_hosts=data.get("known_hosts"),
            metadata=data.get("metadata", {}),
        )


@dataclass
class CommandResult:
    command: str
    stdout: str = ""
    stderr: str = ""
    exit_code: int = 0
    success: bool = True
    error: Optional[str] = None


@dataclass
class DeviceBundle:
    device_name: str
    device_vendor: str
    timestamp: str
    summary: Dict[str, Any]
    raw_outputs: Dict[str, str] = field(default_factory=dict)
    failed_commands: List[str] = field(default_factory=list)


@dataclass
class DeviceIdentity:
    vendor: str = "generic"
    platform: str = "unknown"
    model: str = "unknown"
    confidence: float = 0.0
