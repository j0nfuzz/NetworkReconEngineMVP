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
        "curve25519-sha256@libssh.org",
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

    @staticmethod
    def _transport_is_active(client: Optional[paramiko.SSHClient]) -> bool:
        try:
            return bool(client and client.get_transport() and client.get_transport().is_active())
        except Exception:
            return False

    @staticmethod
    def _channel_state(channel: Optional[paramiko.Channel]) -> Dict[str, object]:
        """Return non-blocking channel state diagnostics for root-cause analysis."""
        if channel is None:
            return {"exists": False}
        try:
            return {
                "exists": True,
                "active": channel.active,
                "eof_received": channel.eof_received,
                "closed": channel.closed,
                "exit_status_ready": channel.exit_status_ready(),
                "recv_ready": channel.recv_ready(),
                "recv_stderr_ready": channel.recv_stderr_ready(),
            }
        except Exception as exc:
            return {"exists": True, "error": str(exc)}

    @staticmethod
    def _transport_state(client: Optional[paramiko.SSHClient]) -> Dict[str, object]:
        """Return non-blocking transport state diagnostics for root-cause analysis."""
        try:
            transport = client.get_transport() if client else None
            if transport is None:
                return {"exists": False}
            return {
                "exists": True,
                "active": transport.is_active(),
                "authenticated": transport.is_authenticated() if hasattr(transport, "is_authenticated") else None,
            }
        except Exception as exc:
            return {"exists": bool(client is not None), "error": str(exc)}

    def _build_original_timeout_result(
        self,
        command: str,
        elapsed: float,
        partial_stdout: str,
        partial_stderr: str,
        client: Optional[paramiko.SSHClient],
        channel: Optional[paramiko.Channel],
    ) -> Dict[str, object]:
        return {
            "command": command,
            "stdout": partial_stdout,
            "stderr": partial_stderr,
            "exit_code": -1,
            "success": False,
            "error": "Command timed out or failed",
            "elapsed_seconds": elapsed,
            "error_type": "timeout",
            "transport_active": self._transport_is_active(client),
            "transport_state": self._transport_state(client),
            "channel_state": self._channel_state(channel),
            "recovery_attempted": False,
            "recovery_successful": None,
        }

    def _try_recover_timeout(
        self,
        command: str,
        original_result: Dict[str, object],
    ) -> Dict[str, object]:
        new_client: Optional[paramiko.SSHClient] = None
        recovered_base = {
            **original_result,
            "original_stdout": original_result.get("stdout"),
            "original_stderr": original_result.get("stderr"),
            "original_elapsed_seconds": original_result.get("elapsed_seconds"),
            "original_error": original_result.get("error"),
            "original_error_type": original_result.get("error_type"),
            "original_transport_active": original_result.get("transport_active"),
            "original_transport_state": original_result.get("transport_state"),
            "original_channel_state": original_result.get("channel_state"),
            "recovery_attempted": True,
        }
        try:
            new_client = self.connect()
            # A timeout recovery must not apply recursively; run without retry.
            retry = self._run_command_once(command, client=new_client, allow_recovery=False)
            recovered = {
                **recovered_base,
                "recovery_successful": retry.get("success", False),
                "retry_elapsed_seconds": retry.get("elapsed_seconds"),
                "retry_exit_code": retry.get("exit_code"),
                "retry_stdout": retry.get("stdout"),
                "retry_stderr": retry.get("stderr"),
                "retry_error": retry.get("error"),
                "retry_error_type": retry.get("error_type"),
                "retry_transport_active": retry.get("transport_active"),
                "retry_transport_state": retry.get("transport_state"),
                "retry_channel_state": retry.get("channel_state"),
                "_recovered_client": new_client if retry.get("success", False) else None,
            }
            if retry.get("success", False):
                recovered["success"] = True
                recovered["stdout"] = retry.get("stdout")
                recovered["stderr"] = retry.get("stderr")
                recovered["exit_code"] = retry.get("exit_code")
                recovered["error"] = retry.get("error")
                recovered["elapsed_seconds"] = retry.get("elapsed_seconds")
                recovered["transport_active"] = retry.get("transport_active")
                recovered["transport_state"] = retry.get("transport_state")
                recovered["channel_state"] = retry.get("channel_state")
            else:
                recovered["error"] = f"Timeout recovery failed: {retry.get('error')}"
                try:
                    new_client.close()
                except Exception:
                    pass
            return recovered
        except Exception as exc:
            if new_client is not None:
                try:
                    new_client.close()
                except Exception:
                    pass
            recovered_base["recovery_successful"] = False
            recovered_base["retry_error"] = f"Recovery connection failed: {exc}"
            recovered_base["error"] = f"Timeout recovery failed: {exc}"
            recovered_base["_recovered_client"] = None
            return recovered_base

    def _run_command_once(
        self,
        command: str,
        *,
        client: Optional[paramiko.SSHClient] = None,
        allow_recovery: bool = True,
    ) -> Dict[str, object]:
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
            channel = stdout.channel if stdout is not None else None
            original_result = self._build_original_timeout_result(
                command, elapsed, partial_stdout, partial_stderr, client, channel
            )
            original_result["error"] = f"Command timed out or failed: {exc}"
            if allow_recovery:
                return self._try_recover_timeout(command, original_result)
            return original_result
        except (EOFError, paramiko.ssh_exception.SSHException, OSError) as exc:
            elapsed = time.perf_counter() - start
            partial_stdout, partial_stderr = self._read_partial_output(stdout, stderr)
            channel = stdout.channel if stdout is not None else None
            return {
                "command": command,
                "stdout": partial_stdout,
                "stderr": partial_stderr,
                "exit_code": -1,
                "success": False,
                "error": f"Command timed out or failed: {exc}",
                "elapsed_seconds": elapsed,
                "error_type": "ssh_exception",
                "transport_active": self._transport_is_active(client),
                "transport_state": self._transport_state(client),
                "channel_state": self._channel_state(channel),
                "recovery_attempted": False,
                "recovery_successful": None,
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
            "transport_active": self._transport_is_active(client),
            "transport_state": self._transport_state(client),
            "channel_state": self._channel_state(stdout.channel if stdout is not None else None),
            "recovery_attempted": False,
            "recovery_successful": None,
        }

    def run_command(
        self,
        command: str,
        *,
        client: Optional[paramiko.SSHClient] = None,
    ) -> Dict[str, object]:
        return self._run_command_once(command, client=client, allow_recovery=True)

    def close(self, client: Optional[paramiko.SSHClient]) -> None:
        if client is None:
            return
        try:
            client.close()
        except Exception:
            pass

    @staticmethod
    def parse_raw_output(output: str) -> List[str]:
        return [line.rstrip() for line in output.splitlines() if line.strip()]
