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

def test_shell_init():
    shell = PcapLabShell()
    assert shell.config['interface'] == 'lo'
    assert len(shell.config['enabled_attacks']) > 0
