import os
import sys
from unittest.mock import MagicMock, patch

import pytest

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from generator.utils.capture import packet_capture


@patch("generator.utils.capture.subprocess.Popen", side_effect=FileNotFoundError())
def test_packet_capture_missing_tcpdump(mock_popen, tmp_path):
    with pytest.raises(RuntimeError, match="tcpdump is not installed"):
        with packet_capture("lo", str(tmp_path / "trace.pcap")):
            pass


@patch("generator.utils.capture.subprocess.Popen")
def test_packet_capture_early_failure(mock_popen, tmp_path):
    process = MagicMock()
    process.poll.return_value = 1
    process.stderr.read.return_value = "permission denied"
    mock_popen.return_value = process

    with pytest.raises(RuntimeError, match="tcpdump failed to start"):
        with packet_capture("lo", str(tmp_path / "trace.pcap")):
            pass
