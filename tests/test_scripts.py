import subprocess
import os
import sys

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
