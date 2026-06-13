import pytest
import sys
import os
from unittest.mock import MagicMock

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from generator.traffic_engine import TrafficEngine
from generator.utils.http_client import TrafficClient

def test_engine_polymorphism_and_di():
    """
    Verify that the engine uses the injected client and handles strategies polymorphically.
    """
    # Mock client to avoid real network calls and sleeps
    mock_client = MagicMock(spec=TrafficClient)
    
    # Initialize engine with 10 requests, 100% attack ratio for easy testing
    engine = TrafficEngine(
        student_id="test_di",
        client=mock_client,
        num_requests=10,
        attack_ratio=1.0,
        enabled_attacks=["sqli"]
    )
    
    results = engine.run()
    
    # Assertions
    assert results["total_requests"] == 10
    assert len(results["attacks"]) == 10
    assert mock_client.execute.call_count == 10
    
    # Check that metadata was correctly collected from the strategies
    for attack in results["attacks"]:
        assert attack["type"] == "SQLI"

def test_engine_normal_traffic_flow():
    """
    Verify that normal traffic doesn't produce attack metadata.
    """
    mock_client = MagicMock(spec=TrafficClient)
    
    # 0% attack ratio
    engine = TrafficEngine(
        student_id="test_normal",
        client=mock_client,
        num_requests=5,
        attack_ratio=0.0
    )
    
    results = engine.run()
    
    assert results["total_requests"] == 5
    assert len(results["attacks"]) == 0
    assert mock_client.execute.call_count == 5
