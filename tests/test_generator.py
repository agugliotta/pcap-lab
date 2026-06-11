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
    
    # Verify exactly 15 requests were sent
    assert mock_session.return_value.request.call_count == 15

