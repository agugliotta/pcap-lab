import pytest
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from generator.utils.seed import init_seed

def test_seed_consistency():
    """Test that the same student ID produces the same seed."""
    seed1 = init_seed("student1@example.com")
    seed2 = init_seed("student1@example.com")
    assert seed1 == seed2

def test_seed_uniqueness():
    """Test that different student IDs produce different seeds."""
    seed1 = init_seed("student1")
    seed2 = init_seed("student2")
    assert seed1 != seed2

def test_seed_stability():
    """Test that the hashing algorithm is stable across runs."""
    # SHA256 of "test" -> int
    # 9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08
    expected_seed = int("9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08", 16)
    actual_seed = init_seed("test")
    assert actual_seed == expected_seed
