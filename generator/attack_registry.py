import json
import importlib
import logging

class AttackRegistry:
    def __init__(self, registry_file="generator/attacks.json"):
        self.registry_file = registry_file
        self.registry = self._load_registry()

    def _load_registry(self):
        try:
            with open(self.registry_file, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logging.error(f"Failed to load attack registry: {e}")
            return {}

    def get_attack_class(self, attack_name):
        class_path = self.registry.get(attack_name)
        if not class_path:
            return None
        
        try:
            module_path, class_name = class_path.rsplit('.', 1)
            module = importlib.import_module(module_path)
            return getattr(module, class_name)
        except (ImportError, AttributeError, ValueError) as e:
            logging.warning(f"Skipping attack '{attack_name}': Could not load {class_path}: {e}")
            return None

    def get_all_attack_names(self):
        return list(self.registry.keys())
