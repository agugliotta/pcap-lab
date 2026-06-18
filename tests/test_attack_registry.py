import pytest
import os
import json
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from generator.attack_registry import AttackRegistry

def test_load_registry(tmp_path):
    # Create a temporary registry file
    registry_file = tmp_path / "attacks.json"
    data = {"test_attack": "generator.attacks.base.BaseAttack"}
    with open(registry_file, "w") as f:
        json.dump(data, f)
    
    registry = AttackRegistry(registry_file=str(registry_file))
    assert "test_attack" in registry.get_all_attack_names()

def test_get_attack_class_invalid():
    registry = AttackRegistry(registry_file="nonexistent.json")
    assert registry.get_attack_class("invalid_attack") is None

def test_get_all_attack_names():
    registry = AttackRegistry()
    names = registry.get_all_attack_names()
    assert isinstance(names, list)
    assert "sqli" in names
    assert "xss" in names
