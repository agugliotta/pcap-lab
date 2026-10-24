import os
import signal
import subprocess
from unittest.mock import MagicMock, patch

import pytest

from generator.utils.capture import packet_capture, _wait_until_ready


def process_mock():
    process = MagicMock()
    process.poll.return_value = None
    process.returncode = 0
    process.communicate.return_value = (None, "")
    return process


@patch("generator.utils.capture.subprocess.Popen", side_effect=FileNotFoundError())
def test_packet_capture_missing_tcpdump(mock_popen, tmp_path):
    with pytest.raises(RuntimeError, match="tcpdump is not installed"):
        with packet_capture("lo", str(tmp_path / "trace.pcap")):
            pass


def test_packet_capture_early_failure():
    process = process_mock()
    process.poll.return_value = 1
    process.stderr.read.return_value = "permission denied"
    with patch("generator.utils.capture.selectors.DefaultSelector"):
        with pytest.raises(RuntimeError, match="tcpdump failed to start.*permission denied"):
            _wait_until_ready(process, "lo")


@patch("generator.utils.capture.os.killpg")
@patch("generator.utils.capture._wait_until_ready")
@patch("generator.utils.capture.subprocess.Popen")
def test_capture_waits_and_flushes(mock_popen, ready, killpg, tmp_path):
    process = process_mock()
    mock_popen.return_value = process
    output = tmp_path / "trace.pcap"
    with packet_capture("lo", str(output)):
        ready.assert_called_once_with(process, "lo")
        output.write_bytes(b"x" * 100)
    killpg.assert_called_once_with(process.pid, signal.SIGINT)
    process.communicate.assert_called_once_with(timeout=3)
    process.stderr.close.assert_called_once()


@pytest.mark.parametrize("failure", ["missing", "empty", "exit", "timeout"])
@patch("generator.utils.capture.os.killpg")
@patch("generator.utils.capture._wait_until_ready")
@patch("generator.utils.capture.subprocess.Popen")
def test_capture_rejects_incomplete_files(mock_popen, ready, killpg, tmp_path, failure):
    process = process_mock()
    mock_popen.return_value = process
    output = tmp_path / "trace.pcap"
    if failure == "exit":
        process.returncode = 1
    if failure == "timeout":
        process.communicate.side_effect = [subprocess.TimeoutExpired("tcpdump", 3), (None, "")]
    with pytest.raises(RuntimeError):
        with packet_capture("lo", str(output)):
            if failure != "missing":
                output.write_bytes(b"x" * (24 if failure == "empty" else 100))
    if failure == "timeout":
        assert killpg.call_args_list[-1].args[1] == signal.SIGKILL


@patch("generator.utils.capture.os.killpg")
@patch("generator.utils.capture._wait_until_ready", side_effect=RuntimeError("not ready"))
@patch("generator.utils.capture.subprocess.Popen")
def test_capture_stops_on_startup_timeout(mock_popen, ready, killpg, tmp_path):
    process = process_mock()
    mock_popen.return_value = process
    with pytest.raises(RuntimeError, match="not ready"):
        with packet_capture("lo", str(tmp_path / "trace.pcap")):
            pytest.fail("Traffic must not start")
    process.communicate.assert_called_once()
