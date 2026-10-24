import json
import importlib
import logging
from pathlib import Path

class AttackRegistry:
    """
    Manages dynamic loading of attack strategies defined in a JSON configuration file.
    
    This class acts as a factory, resolving attack identifiers to their corresponding
    Python implementation classes at runtime, allowing for easy expansion of the
    attack library without modifying the core engine logic.
    """

    def __init__(self, registry_file=None):
        """
        Initializes the registry by loading the mapping from the specified file.
        
        Args:
            registry_file (str): Path to the JSON file containing attack mappings.
        """
        self.registry_file = registry_file if registry_file is not None else Path(__file__).with_name("attacks.json")
        self.registry = self._load_registry()

    def _load_registry(self):
        """
        Loads the JSON registry file into a dictionary.
        
        Returns:
            dict: The loaded attack mappings, or an empty dict if loading fails.
        """
        try:
            registry_path = Path(self.registry_file)
            with open(registry_path, 'r') as f:
                registry = json.load(f)
            if not isinstance(registry, dict) or not all(isinstance(k, str) and isinstance(v, str) for k, v in registry.items()):
                raise ValueError("Attack registry must map names to class paths.")
            return registry
        except (OSError, ValueError) as e:
            logging.error(f"Failed to load attack registry: {e}")
            return {}

    def get_attack_class(self, attack_name):
        """
        Resolves an attack name to its corresponding Python class.
        
        Args:
            attack_name (str): The short key for the attack (e.g., 'sqli').
            
        Returns:
            Type: The attack class if found and importable, otherwise None.
        """
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
        """
        Returns a list of all registered attack keys.
        
        Returns:
            list: A list of available attack names.
        """
        return list(self.registry.keys())
