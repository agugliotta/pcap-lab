import pytest
import os
import sys
from unittest.mock import MagicMock, patch

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from generator.shell import PcapLabShell

@patch('questionary.select')
@patch('questionary.text')
@patch('questionary.path')
def test_shell_configuration(mock_path, mock_text, mock_select):
    """
    Test that the shell configuration updates correctly.
    """
    shell = PcapLabShell()
    
    # Mocking choices
    mock_select.return_value.ask.side_effect = ["Student List: ", "Back"]
    mock_text.return_value.ask.return_value = "student1,student2"
    
    # Run configuration
    shell.configure()
    
    assert shell.config['student_list'] == "student1,student2"

@patch('generator.shell.default_interface', return_value='lo0')
def test_shell_init(mock_default_interface):
    shell = PcapLabShell()
    assert shell.config['interface'] == 'lo0'
    assert len(shell.config['enabled_attacks']) > 0

def test_shell_config_summary(capsys):
    shell = PcapLabShell()
    shell.config["student_list"] = "alice,bob"
    shell.config["student_file"] = "students.txt"
    shell.config["interface"] = "lo0"

    shell.print_config_summary()

    output = capsys.readouterr().out
    assert "Current configuration" in output
    assert "Students: inline list, file" in output
    assert "Interface: lo0" in output

@patch('generator.shell.time.sleep', return_value=None)
@patch('questionary.select')
@patch('questionary.text')
def test_shell_rejects_invalid_requests(mock_text, mock_select, mock_sleep):
    shell = PcapLabShell()

    mock_select.return_value.ask.side_effect = ["Requests: 50", "Back"]
    mock_text.return_value.ask.return_value = "0"

    shell.configure()

    assert shell.config["requests"] == 50

@patch('generator.shell.time.sleep', return_value=None)
@patch('questionary.select')
@patch('questionary.text')
def test_shell_rejects_invalid_attack_ratio(mock_text, mock_select, mock_sleep):
    shell = PcapLabShell()

    mock_select.return_value.ask.side_effect = ["Attack Ratio: 0.3", "Back"]
    mock_text.return_value.ask.return_value = "1.5"

    shell.configure()

    assert shell.config["attack_ratio"] == 0.3

@patch('generator.shell.interface_exists', return_value=False)
@patch('builtins.input', return_value='')
@patch('questionary.select')
def test_shell_rejects_invalid_interface(mock_select, mock_input, mock_interface_exists):
    shell = PcapLabShell()
    shell.config["student_list"] = "alice"
    shell.config["interface"] = "bad0"

    mock_select.return_value.ask.side_effect = ["Run Generation", "Quit"]

    shell.run_menu()

    mock_interface_exists.assert_called_once_with("bad0")
