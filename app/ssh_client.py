from __future__ import annotations

import socket
import struct
import time
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

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

    @staticmethod
    def get_supported_kex_algorithms() -> List[str]:
        """Return the KEX algorithms Paramiko currently prefers/supports."""
        preferred = getattr(paramiko.Transport, "_preferred_kex", None)
        if preferred is not None:
            return list(preferred)
        return list(getattr(paramiko.Transport, "_kex_info", {}).keys())

    @staticmethod
    def _parse_name_list(packet: bytes, offset: int) -> tuple[List[str], int]:
        """Parse an RFC 4251 `name-list` starting at offset. Returns (names, new_offset)."""
        if len(packet) < offset + 4:
            return [], offset
        length = struct.unpack(">I", packet[offset : offset + 4])[0]
        offset += 4
        if length == 0 or len(packet) < offset + length:
            return [], offset
        names = packet[offset : offset + length].decode("utf-8", errors="replace")
        offset += length
        return [name.strip() for name in names.split(",") if name.strip()], offset

    @staticmethod
    def _extract_peer_kex_from_init(remote_kex_init: Optional[bytes]) -> Optional[List[str]]:
        """Extract the peer's offered KEX algorithms from a raw SSH_MSG_KEXINIT packet."""
        if not remote_kex_init:
            return None
        # SSH_MSG_KEXINIT = 20 (1 byte), 16 byte cookie, then name-lists.
        # KEX algorithms is the first name-list.
        if len(remote_kex_init) < 17 or remote_kex_init[0] != 20:
            return None
        offset = 17
        kex_algorithms, _ = DeviceSSHClient._parse_name_list(remote_kex_init, offset)
        return kex_algorithms if kex_algorithms else None

    @classmethod
    def get_peer_kex_algorithms(
        cls,
        hostname: str,
        port: int = 22,
        timeout: int = 15,
    ) -> Optional[List[str]]:
        """Attempt a transport-level handshake to capture the peer's offered KEX list.

        This deliberately avoids host-key verification or authentication.  Any failure
        returns ``None`` so that diagnostics degrade gracefully when the peer cannot be
        probed.
        """
        sock: Optional[socket.socket] = None
        transport: Optional[paramiko.Transport] = None
        try:
            sock = socket.create_connection((hostname, port), timeout=timeout)
            transport = paramiko.Transport(sock)
            transport.start_client(timeout=timeout)
            return cls._extract_peer_kex_from_init(getattr(transport, "remote_kex_init", None))
        except Exception:
            # Try to salvage the peer KEX init even if negotiation failed.
            if transport is not None:
                peer_kex = cls._extract_peer_kex_from_init(getattr(transport, "remote_kex_init", None))
                if peer_kex:
                    return peer_kex
            return None
        finally:
            if transport is not None:
                try:
                    transport.close()
                except Exception:
                    pass
            if sock is not None:
                try:
                    sock.close()
                except Exception:
                    pass

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
    def _is_kex_error(message: str) -> bool:
        lowered = message.lower()
        return (
            "no acceptable kex algorithm" in lowered
            or "group14-sha1" in lowered
            or "group1-sha1" in lowered
            or ("keyerror" in lowered and "kex" in lowered)
        )

    @classmethod
    def explain_compatibility_error(
        cls,
        exc: Exception,
        *,
        peer_kex_algorithms: Optional[Sequence[str]] = None,
    ) -> str:
        message = str(exc)
        supported = cls.get_supported_kex_algorithms()
        supported_text = ", ".join(supported) if supported else "(unknown)"
        peer_text = ", ".join(peer_kex_algorithms) if peer_kex_algorithms else "(could not be obtained)"

        if cls._is_kex_error(message):
            return (
                "SSH key exchange negotiation failed. "
                f"Supported KEX algorithms: {supported_text}. "
                f"Peer offered KEX algorithms: {peer_text}. "
                "No common algorithm was found. The device may only support older SHA1-based KEX algorithms "
                "that Paramiko no longer enables by default. Use a legacy Paramiko profile (requirements-legacy.txt) "
                "or update the device's SSH configuration."
            )
        return message

    def probe(self) -> Dict[str, object]:
        try:
            client = self.connect()
            self.close(client)
            return {"reachable": True, "status": "connected"}
        except (socket.timeout, TimeoutError, paramiko.SSHException, OSError, KeyError, RuntimeError) as exc:
            peer_kex = None
            if self._is_kex_error(str(exc)):
                peer_kex = self.get_peer_kex_algorithms(self.hostname, self.port, self.timeout)
            return {
                "reachable": False,
                "status": "unreachable",
                "error": self.explain_compatibility_error(exc, peer_kex_algorithms=peer_kex),
            }
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
                if self._is_kex_error(message):
                    if attempt == 0:
                        self._apply_ssh_compatibility_settings()
                        continue
                    peer_kex = self.get_peer_kex_algorithms(self.hostname, self.port, self.timeout)
                    raise type(exc)(self.explain_compatibility_error(exc, peer_kex_algorithms=peer_kex))
                raise
            except Exception:
                raise

        if last_error is not None:
            raise last_error
        raise RuntimeError("SSH connection failed without a reported error.")

    @staticmethod
    def _read_partial_output(
        stdout: Optional[paramiko.ChannelFile],
        stderr: Optional[paramiko.ChannelFile],
    ) -> Tuple[str, str]:
        """Attempt to recover any stdout/stderr already buffered before an exception."""
        partial_stdout = ""
        partial_stderr = ""

        if stdout is not None and stdout.channel is not None:
            try:
                channel = stdout.channel
                chunks = []
                while channel.recv_ready():
                    chunk = channel.recv(65536)
                    if not chunk:
                        break
                    chunks.append(chunk)
                if chunks:
                    partial_stdout = b"".join(chunks).decode("utf-8", errors="replace")
            except Exception:
                pass

        if stderr is not None and stderr.channel is not None:
            try:
                channel = stderr.channel
                chunks = []
                while channel.recv_stderr_ready():
                    chunk = channel.recv_stderr(65536)
                    if not chunk:
                        break
                    chunks.append(chunk)
                if chunks:
                    partial_stderr = b"".join(chunks).decode("utf-8", errors="replace")
            except Exception:
                pass

        return partial_stdout, partial_stderr

    def run_command(self, command: str, *, client: Optional[paramiko.SSHClient] = None) -> Dict[str, object]:
        if client is None:
            client = self.connect()

        start = time.perf_counter()
        stdout: Optional[paramiko.ChannelFile] = None
        stderr: Optional[paramiko.ChannelFile] = None

        try:
            stdin, stdout, stderr = client.exec_command(command, timeout=self.timeout)
            # Drain stdout/stderr before blocking on the exit status to avoid a
            # deadlock on large command output.
            stdout_data = stdout.read().decode("utf-8", errors="replace")
            stderr_data = stderr.read().decode("utf-8", errors="replace")
            exit_code = stdout.channel.recv_exit_status()
        except (socket.timeout, TimeoutError) as exc:
            elapsed = time.perf_counter() - start
            partial_stdout, partial_stderr = self._read_partial_output(stdout, stderr)
            return {
                "command": command,
                "stdout": partial_stdout,
                "stderr": partial_stderr,
                "exit_code": -1,
                "success": False,
                "error": f"Command timed out or failed: {exc}",
                "elapsed_seconds": elapsed,
                "error_type": "timeout",
            }
        except (EOFError, paramiko.ssh_exception.SSHException, OSError) as exc:
            elapsed = time.perf_counter() - start
            partial_stdout, partial_stderr = self._read_partial_output(stdout, stderr)
            return {
                "command": command,
                "stdout": partial_stdout,
                "stderr": partial_stderr,
                "exit_code": -1,
                "success": False,
                "error": f"Command timed out or failed: {exc}",
                "elapsed_seconds": elapsed,
                "error_type": "ssh_exception",
            }

        elapsed = time.perf_counter() - start
        return {
            "command": command,
            "stdout": stdout_data,
            "stderr": stderr_data,
            "exit_code": exit_code,
            "success": exit_code == 0,
            "error": stderr_data if exit_code != 0 else None,
            "elapsed_seconds": elapsed,
        }

    def close(self, client: paramiko.SSHClient) -> None:
        try:
            client.close()
        except Exception:
            pass

    @staticmethod
    def parse_raw_output(output: str) -> List[str]:
        return [line.rstrip() for line in output.splitlines() if line.strip()]
