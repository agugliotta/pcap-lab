import subprocess
import os
import sys
from click.testing import CliRunner
from unittest.mock import patch

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import main

def test_main_generate_usage():
    """Verify that the main generate command shows usage when no arguments are provided."""
    # Use sys.executable to ensure we use the same python environment
    result = subprocess.run([sys.executable, "main.py", "generate", "--help"], capture_output=True, text=True)
    assert result.returncode == 0
    assert "Usage: main.py generate" in result.stdout
    assert "--requests" in result.stdout
    assert "--attack-count" in result.stdout
    assert "--attack-ratio" in result.stdout
    assert "--obfuscation" in result.stdout



def test_main_replay_usage():
    """Verify that the main replay command shows usage when no arguments are provided."""
    result = subprocess.run([sys.executable, "main.py", "replay", "--help"], capture_output=True, text=True)
    assert result.returncode == 0
    assert "Usage: main.py replay" in result.stdout


@patch("generator.pcap_generator.PcapGenerator.generate_batch", side_effect=RuntimeError("tcpdump failed to start on interface lo: Permission denied"))
@patch("main.interface_exists", return_value=True)
@patch("main.os.geteuid", return_value=0)
def test_main_generate_reports_capture_error(mock_geteuid, mock_interface_exists, mock_generate_batch):
    runner = CliRunner()

    result = runner.invoke(main.cli, ["generate", "alice", "lo0"])

    assert result.exit_code == 1
    assert "Error during generation" in result.output
    assert "Hint: install tcpdump" in result.output


@patch("generator.pcap_generator.PcapGenerator.generate_batch")
@patch("main.interface_exists", return_value=True)
@patch("main.os.geteuid", return_value=0)
def test_main_generate_warns_on_unknown_attacks(mock_geteuid, mock_interface_exists, mock_generate_batch):
    runner = CliRunner()

    result = runner.invoke(main.cli, ["generate", "alice", "lo0", "--attacks", "sqli,unknown"])

    assert result.exit_code == 0
    assert "Warning: unknown attack type(s) ignored: unknown" in result.output
    assert "Available attacks:" in result.output


@patch("main.interface_exists", return_value=False)
@patch("main.os.geteuid", return_value=0)
def test_main_generate_rejects_invalid_interface(mock_geteuid, mock_interface_exists):
    runner = CliRunner()

    result = runner.invoke(main.cli, ["generate", "alice", "bad0"])

    assert result.exit_code == 1
    assert "Error: interface 'bad0' does not exist on this machine." in result.output
