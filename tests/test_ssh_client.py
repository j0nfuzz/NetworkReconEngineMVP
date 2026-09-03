"""Tests for PHASE-036 timeout/session root-cause instrumentation in app.ssh_client."""
from __future__ import annotations

import socket

import paramiko
import pytest

from app.ssh_client import DeviceSSHClient


def test_timeout_result_includes_channel_and_transport_state():
    class FakeChannel:
        active = True
        eof_received = False
        closed = False

        def exit_status_ready(self):
            return False

        def recv_ready(self):
            return False

        def recv_stderr_ready(self):
            return False

    class FakeStdout:
        channel = FakeChannel()

        def read(self):
            raise socket.timeout("Command timed out")

    class FakeStderr:
        channel = FakeChannel()

        def read(self):
            return b""

    class FakeTransport:
        def is_active(self):
            return True

        def is_authenticated(self):
            return True

    class FakeSSHClient:
        _transport = FakeTransport()

        def exec_command(self, command, timeout=None):
            return None, FakeStdout(), FakeStderr()

        def get_transport(self):
            return self._transport

    client = DeviceSSHClient("device.example", "user", "pass")
    result = client.run_command("show version", client=FakeSSHClient())

    assert result["error_type"] == "timeout"
    assert result["channel_state"]["exists"] is True
    assert result["channel_state"]["active"] is True
    assert result["transport_state"]["exists"] is True
    assert result["transport_state"]["active"] is True
    assert result["transport_state"]["authenticated"] is True


def test_ssh_exception_result_includes_channel_and_transport_state():
    class FakeChannel:
        active = False
        eof_received = True
        closed = True

        def exit_status_ready(self):
            return False

        def recv_ready(self):
            return False

        def recv_stderr_ready(self):
            return False

    class FakeStdout:
        channel = FakeChannel()

        def read(self):
            raise paramiko.SSHException("channel closed")

    class FakeStderr:
        channel = FakeChannel()

        def read(self):
            return b""

    class FakeTransport:
        def is_active(self):
            return False

        def is_authenticated(self):
            return False

    class FakeSSHClient:
        _transport = FakeTransport()

        def exec_command(self, command, timeout=None):
            return None, FakeStdout(), FakeStderr()

        def get_transport(self):
            return self._transport

    client = DeviceSSHClient("device.example", "user", "pass")
    result = client.run_command("show version", client=FakeSSHClient())

    assert result["error_type"] == "ssh_exception"
    assert result["channel_state"]["closed"] is True
    assert result["transport_state"]["active"] is False
    assert result["transport_state"]["authenticated"] is False


def test_success_result_includes_channel_and_transport_state():
    class FakeChannel:
        def recv_exit_status(self):
            return 0

        active = True
        eof_received = False
        closed = False

        def exit_status_ready(self):
            return True

        def recv_ready(self):
            return False

        def recv_stderr_ready(self):
            return False

    class FakeTransport:
        def is_active(self):
            return True

        def is_authenticated(self):
            return True

    class FakeStdout:
        channel = FakeChannel()

        def read(self):
            return b"ok"

    class FakeStderr:
        channel = FakeChannel()

        def read(self):
            return b""

    class FakeSSHClient:
        _transport = FakeTransport()

        def exec_command(self, command, timeout=None):
            return None, FakeStdout(), FakeStderr()

        def get_transport(self):
            return self._transport

    client = DeviceSSHClient("device.example", "user", "pass")
    result = client.run_command("show version", client=FakeSSHClient())

    assert result["success"] is True
    assert result["channel_state"]["exists"] is True
    assert result["transport_state"]["active"] is True


def test_channel_state_gracefully_handles_missing_channel():
    assert DeviceSSHClient._channel_state(None) == {"exists": False}


def test_transport_state_gracefully_handles_missing_client():
    assert DeviceSSHClient._transport_state(None) == {"exists": False}


def test_successful_timeout_recovery_refreshes_channel_and_transport_state():
    class OriginalChannel:
        active = False
        eof_received = True
        closed = True

        def exit_status_ready(self):
            return True

        def recv_ready(self):
            return False

        def recv_stderr_ready(self):
            return False

    class RecoveredChannel:
        active = True
        eof_received = False
        closed = False

        def recv_exit_status(self):
            return 0

        def exit_status_ready(self):
            return True

        def recv_ready(self):
            return False

        def recv_stderr_ready(self):
            return False

    class OriginalTransport:
        def is_active(self):
            return False

        def is_authenticated(self):
            return False

    class RecoveredTransport:
        def is_active(self):
            return True

        def is_authenticated(self):
            return True

    class TimeoutStdout:
        channel = OriginalChannel()

        def read(self):
            raise socket.timeout("Command timed out")

    class EmptyStderr:
        channel = OriginalChannel()

        def read(self):
            return b""

    class SucceedingStdout:
        channel = RecoveredChannel()

        def read(self):
            return b"recovered output"

    class SucceedingStderr:
        channel = RecoveredChannel()

        def read(self):
            return b""

    class OriginalSSHClient:
        _transport = OriginalTransport()

        def exec_command(self, command, timeout=None):
            return None, TimeoutStdout(), EmptyStderr()

        def get_transport(self):
            return self._transport

    class RecoveredSSHClient:
        _transport = RecoveredTransport()

        def exec_command(self, command, timeout=None):
            return None, SucceedingStdout(), SucceedingStderr()

        def get_transport(self):
            return self._transport

    client = DeviceSSHClient("device.example", "user", "pass")
    call_count = [0]

    def fake_connect():
        call_count[0] += 1
        return RecoveredSSHClient()

    client.connect = fake_connect
    result = client.run_command("show version", client=OriginalSSHClient())

    assert result["success"] is True
    assert result["recovery_attempted"] is True
    assert result["recovery_successful"] is True
    assert result["stdout"] == "recovered output"
    assert result["original_channel_state"]["active"] is False
    assert result["original_channel_state"]["closed"] is True
    assert result["original_transport_state"]["active"] is False
    assert result["retry_channel_state"]["active"] is True
    assert result["retry_channel_state"]["closed"] is False
    assert result["retry_transport_state"]["active"] is True
    assert result["retry_transport_state"]["authenticated"] is True
    assert result["channel_state"]["active"] is True
    assert result["channel_state"]["closed"] is False
    assert result["transport_state"]["active"] is True
    assert result["transport_state"]["authenticated"] is True


def test_failed_timeout_recovery_preserves_original_channel_and_transport_state():
    class OriginalChannel:
        active = False
        eof_received = True
        closed = True

        def exit_status_ready(self):
            return True

        def recv_ready(self):
            return False

        def recv_stderr_ready(self):
            return False

    class RecoveredChannel:
        active = False
        eof_received = False
        closed = True

        def recv_exit_status(self):
            return -1

        def exit_status_ready(self):
            return False

        def recv_ready(self):
            return False

        def recv_stderr_ready(self):
            return False

    class OriginalTransport:
        def is_active(self):
            return False

        def is_authenticated(self):
            return False

    class RecoveredTransport:
        def is_active(self):
            return False

        def is_authenticated(self):
            return False

    class TimeoutStdout:
        channel = OriginalChannel()

        def read(self):
            raise socket.timeout("Command timed out")

    class EmptyStderr:
        channel = OriginalChannel()

        def read(self):
            return b""

    class FailingStdout:
        channel = RecoveredChannel()

        def read(self):
            raise socket.timeout("Command timed out again")

    class FailingStderr:
        channel = RecoveredChannel()

        def read(self):
            return b""

    class OriginalSSHClient:
        _transport = OriginalTransport()

        def exec_command(self, command, timeout=None):
            return None, TimeoutStdout(), EmptyStderr()

        def get_transport(self):
            return self._transport

    class RecoveredSSHClient:
        _transport = RecoveredTransport()

        def exec_command(self, command, timeout=None):
            return None, FailingStdout(), FailingStderr()

        def get_transport(self):
            return self._transport

    client = DeviceSSHClient("device.example", "user", "pass")
    client.connect = lambda: RecoveredSSHClient()
    result = client.run_command("show version", client=OriginalSSHClient())

    assert result["success"] is False
    assert result["recovery_attempted"] is True
    assert result["recovery_successful"] is False
    assert result["original_channel_state"]["active"] is False
    assert result["original_channel_state"]["closed"] is True
    assert result["original_transport_state"]["active"] is False
    assert result["retry_channel_state"]["active"] is False
    assert result["retry_channel_state"]["closed"] is True
    assert result["retry_transport_state"]["active"] is False
    assert result["channel_state"]["active"] is False
    assert result["channel_state"]["closed"] is True
    assert result["transport_state"]["active"] is False


def test_timeout_recovery_connection_failure_preserves_original_state():
    class OriginalChannel:
        active = False
        eof_received = True
        closed = True

        def recv_exit_status(self):
            return -1

        def exit_status_ready(self):
            return True

        def recv_ready(self):
            return False

        def recv_stderr_ready(self):
            return False

    class OriginalTransport:
        def is_active(self):
            return False

        def is_authenticated(self):
            return False

    class TimeoutStdout:
        channel = OriginalChannel()

        def read(self):
            raise socket.timeout("Command timed out")

    class EmptyStderr:
        channel = OriginalChannel()

        def read(self):
            return b""

    class OriginalSSHClient:
        _transport = OriginalTransport()

        def exec_command(self, command, timeout=None):
            return None, TimeoutStdout(), EmptyStderr()

        def get_transport(self):
            return self._transport

    client = DeviceSSHClient("device.example", "user", "pass")
    client.connect = lambda: (_ for _ in ()).throw(paramiko.SSHException("dead"))
    result = client.run_command("show version", client=OriginalSSHClient())

    assert result["success"] is False
    assert result["recovery_attempted"] is True
    assert result["recovery_successful"] is False
    assert result["original_channel_state"]["closed"] is True
    assert result["original_transport_state"]["active"] is False
    assert result["channel_state"]["closed"] is True
    assert result["transport_state"]["active"] is False
