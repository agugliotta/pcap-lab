import pytest
import os
import json
import sys
from unittest.mock import MagicMock, patch

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from generator.traffic_engine import TrafficEngine

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
    with patch('generator.traffic_engine.MIN_REQUESTS', 5), \
         patch('generator.traffic_engine.MAX_REQUESTS', 10):
        
        engine = TrafficEngine("test_student_unit")
        result = engine.run()
        
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
    engine = TrafficEngine("test_student_unit", num_requests=15)
    result = engine.run()
    
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
    
    engine = TrafficEngine("test_student_unit", num_requests=20, attack_count=5)
    result = engine.run()
    
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
    engine = TrafficEngine("test_student_unit", num_requests=20, attack_ratio=0.25)
    result = engine.run()
    
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
    engine = TrafficEngine("test_student_unit", num_requests=10, attack_count=3, attack_ratio=0.5)
    result = engine.run()
    
    assert result["total_requests"] == 10
    assert len(result["attacks"]) == 3

@patch('requests.Session')
def test_traffic_logic_enabled_attacks(mock_session):
    """
    Test that enabling specific attacks works and only those are generated.
    """
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_session.return_value.request.return_value = mock_resp
    
    enabled = ["rce", "lfi", "cmdi"]
    engine = TrafficEngine("test_student_unit", num_requests=30, attack_count=10, enabled_attacks=enabled)
    result = engine.run()
    
    assert len(result["attacks"]) == 10
    for attack in result["attacks"]:
        assert attack["type"] in ["RCE", "LFI", "CMDI"]
