import subprocess
import os

def test_replay_script_usage():
    """Verify that the replay script shows usage when no arguments are provided."""
    script_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "scripts", "replay.sh")
    result = subprocess.run([script_path], capture_output=True, text=True)
    assert result.returncode == 1
    assert "Usage:" in result.stdout

def test_generate_script_usage():
    """Verify that the generate script shows usage when no arguments are provided."""
    script_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "scripts", "generate.sh")
    result = subprocess.run([script_path], capture_output=True, text=True)
    assert result.returncode == 1
    assert "Usage:" in result.stdout
