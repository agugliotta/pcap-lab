import pytest
import os
import json
import sys
from unittest.mock import MagicMock, patch

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from generator.generate_pcap import run_traffic

@patch('requests.Session')
def test_traffic_logic(mock_session):
    """
    Test the main traffic generation logic without network calls.
    """
    # Mock response
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_session.return_value.request.return_value = mock_resp
    
    # Run a small batch
    with patch('generator.generate_pcap.MIN_REQUESTS', 5), \
         patch('generator.generate_pcap.MAX_REQUESTS', 10):
        
        result = run_traffic("test_student_unit")
        
        assert "seed" in result
        assert result["total_requests"] >= 5
        assert result["total_requests"] <= 10
        assert isinstance(result["attacks"], list)
        assert "settings" in result
        assert result["settings"]["num_requests"] is None
        assert isinstance(result["settings"]["enabled_attacks"], list)
        
        # Verify requests were 'sent'
        assert mock_session.return_value.request.called

@patch('requests.Session')
def test_traffic_logic_exact_requests(mock_session):
    """
    Test the traffic generation logic with an exact number of requests.
    """
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_session.return_value.request.return_value = mock_resp
    
    # Run with exact requests
    result = run_traffic("test_student_unit", num_requests=15)
    
    assert "seed" in result
    assert result["total_requests"] == 15
    assert len(result["attacks"]) <= 15
    assert isinstance(result["attacks"], list)
    assert "settings" in result
    assert result["settings"]["num_requests"] == 15
    assert isinstance(result["settings"]["enabled_attacks"], list)
    
    # Verify exactly 15 requests were sent
    assert mock_session.return_value.request.call_count == 15

@patch('requests.Session')
def test_traffic_logic_exact_attack_count(mock_session):
    """
    Test that specifying an exact attack count results in exactly that many attacks.
    """
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_session.return_value.request.return_value = mock_resp
    
    result = run_traffic("test_student_unit", num_requests=20, attack_count=5)
    
    assert result["total_requests"] == 20
    # The length of the attacks list in answer key should be exactly 5
    assert len(result["attacks"]) == 5
    assert result["settings"]["attack_count"] == 5
    assert result["settings"]["attack_ratio"] is None

@patch('requests.Session')
def test_traffic_logic_attack_ratio(mock_session):
    """
    Test that specifying an attack ratio results in the correct number of attacks.
    """
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_session.return_value.request.return_value = mock_resp
    
    # 20 requests * 0.25 ratio = 5 attacks
    result = run_traffic("test_student_unit", num_requests=20, attack_ratio=0.25)
    
    assert result["total_requests"] == 20
    assert len(result["attacks"]) == 5
    assert result["settings"]["attack_ratio"] == 0.25
    assert result["settings"]["attack_count"] is None

@patch('requests.Session')
def test_traffic_logic_priority(mock_session):
    """
    Test that when both attack_count and attack_ratio are specified, count takes priority.
    """
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_session.return_value.request.return_value = mock_resp
    
    # Count (3) should take priority over ratio (0.5 * 10 = 5)
    result = run_traffic("test_student_unit", num_requests=10, attack_count=3, attack_ratio=0.5)
    
    assert result["total_requests"] == 10
    assert len(result["attacks"]) == 3

@patch('requests.Session')
def test_traffic_logic_validation(mock_session):
    """
    Test that invalid attack counts or ratios raise ValueError.
    """
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_session.return_value.request.return_value = mock_resp
    
    # attack_count > num_requests
    with pytest.raises(ValueError):
        run_traffic("test_student_unit", num_requests=10, attack_count=11)
        
    # attack_count < 0
    with pytest.raises(ValueError):
        run_traffic("test_student_unit", num_requests=10, attack_count=-1)
        
    # attack_ratio < 0
    with pytest.raises(ValueError):
        run_traffic("test_student_unit", num_requests=10, attack_ratio=-0.1)
        
    # attack_ratio > 1
    with pytest.raises(ValueError):
        run_traffic("test_student_unit", num_requests=10, attack_ratio=1.1)



