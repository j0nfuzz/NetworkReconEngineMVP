from __future__ import annotations

import socket
from pathlib import Path
from typing import Dict, List, Optional

import paramiko


class DeviceSSHClient:
    COMPATIBLE_KEX_ALGORITHMS = (
        "diffie-hellman-group14-sha1",
        "diffie-hellman-group1-sha1",
        "diffie-hellman-group-exchange-sha1",
        "diffie-hellman-group14-sha256",
        "diffie-hellman-group16-sha512",
        "diffie-hellman-group-exchange-sha256",
        "person@example.com",
    )

    @staticmethod
    def _apply_ssh_compatibility_settings() -> None:
        supported = set(getattr(paramiko.Transport, "_kex_info", {}).keys())
        preferred = list(getattr(paramiko.Transport, "_preferred_kex", ()))
        for algorithm in DeviceSSHClient.COMPATIBLE_KEX_ALGORITHMS:
            if algorithm in supported and algorithm not in preferred:
                preferred.append(algorithm)
        paramiko.Transport._preferred_kex = tuple(preferred)

    def __init__(
        self,
        hostname: str,
        username: str,
        password: str,
        port: int = 22,
        timeout: int = 15,
        host_key_policy: str = "auto",
        known_hosts: Optional[str] = None,
    ):
        self.hostname = hostname
        self.username = username
        self.password = password
        self.port = port
        self.timeout = timeout
        self.host_key_policy = host_key_policy
        self.known_hosts = known_hosts
        self._apply_ssh_compatibility_settings()

    def _apply_host_key_policy(self, client: "paramiko.SSHClient") -> None:
        """Configure how unknown host keys are handled on the given SSH client."""
        if self.known_hosts:
            # Known_hosts mode implies strict verification: refuse unknown hosts.
            known_hosts_path = Path(self.known_hosts)
            if known_hosts_path.exists():
                client.load_host_keys(str(known_hosts_path))
            client.load_system_host_keys()
            client.set_missing_host_key_policy(paramiko.RejectPolicy())
            return

        if self.host_key_policy == "reject":
            client.set_missing_host_key_policy(paramiko.RejectPolicy())
        elif self.host_key_policy == "warning":
            client.set_missing_host_key_policy(paramiko.WarningPolicy())
        else:  # "auto" (default) - trust and remember new host keys
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    @staticmethod
    def explain_compatibility_error(exc: Exception) -> str:
        message = str(exc)
        lowered = message.lower()
        if "no acceptable kex algorithm" in lowered or "group14-sha1" in lowered or "group1-sha1" in lowered:
            return (
                "SSH key exchange negotiation failed. This often happens when the target device is older or only "
                "accepts older SHA1-based key exchange algorithms. Paramiko 5.x supports the current modern KEX "
                "set, so the device may require a newer SSH profile or a different access path."
            )
        if "keyerror" in lowered and "kex" in lowered:
            return (
                "SSH KEX negotiation failed because the server selected an algorithm that Paramiko does not support "
                "for this session. The device may be using an older or restricted SSH policy."
            )
        return message

    def probe(self) -> Dict[str, object]:
        try:
            client = self.connect()
            self.close(client)
            return {"reachable": True, "status": "connected"}
        except (socket.timeout, TimeoutError, paramiko.SSHException, OSError, KeyError, RuntimeError) as exc:
            return {"reachable": False, "status": "unreachable", "error": self.explain_compatibility_error(exc)}
        except Exception as exc:
            return {"reachable": False, "status": "unreachable", "error": str(exc)}

    def connect(self) -> paramiko.SSHClient:
        last_error = None
        for attempt in range(2):
            try:
                client = paramiko.SSHClient()
                self._apply_host_key_policy(client)
                client.connect(
                    hostname=self.hostname,
                    username=self.username,
                    password=self.password,
                    port=self.port,
                    timeout=self.timeout,
                    banner_timeout=self.timeout,
                    auth_timeout=self.timeout,
                )
                return client
            except (paramiko.SSHException, KeyError) as exc:
                last_error = exc
                message = str(exc).lower()
                if "no acceptable kex algorithm" in message or "group14-sha1" in message or "group1-sha1" in message or "keyerror" in message:
                    if attempt == 0:
                        self._apply_ssh_compatibility_settings()
                        continue
                    raise
                raise
            except Exception:
                raise

        if last_error is not None:
            raise last_error
        raise RuntimeError("SSH connection failed without a reported error.")

    def run_command(self, command: str, *, client: Optional[paramiko.SSHClient] = None) -> Dict[str, object]:
        if client is None:
            client = self.connect()

        try:
            stdin, stdout, stderr = client.exec_command(command, timeout=self.timeout)
            # Drain stdout/stderr before blocking on the exit status to avoid a
            # deadlock on large command output.
            stdout_data = stdout.read().decode("utf-8", errors="replace")
            stderr_data = stderr.read().decode("utf-8", errors="replace")
            exit_code = stdout.channel.recv_exit_status()
        except (socket.timeout, TimeoutError, EOFError, paramiko.ssh_exception.SSHException, OSError) as exc:
            return {
                "command": command,
                "stdout": "",
                "stderr": "",
                "exit_code": -1,
                "success": False,
                "error": f"Command timed out or failed: {exc}",
            }

        return {
            "command": command,
            "stdout": stdout_data,
            "stderr": stderr_data,
            "exit_code": exit_code,
            "success": exit_code == 0,
            "error": stderr_data if exit_code != 0 else None,
        }

    def close(self, client: paramiko.SSHClient) -> None:
        try:
            client.close()
        except Exception:
            pass

    @staticmethod
    def parse_raw_output(output: str) -> List[str]:
        return [line.rstrip() for line in output.splitlines() if line.strip()]
