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

    def __init__(self, registry_file="generator/attacks.json"):
        """
        Initializes the registry by loading the mapping from the specified file.
        
        Args:
            registry_file (str): Path to the JSON file containing attack mappings.
        """
        self.registry_file = registry_file
        self.registry = self._load_registry()

    def _load_registry(self):
        """
        Loads the JSON registry file into a dictionary.
        
        Returns:
            dict: The loaded attack mappings, or an empty dict if loading fails.
        """
        try:
            registry_path = Path(self.registry_file)
            if not registry_path.is_absolute() and not registry_path.exists():
                registry_path = Path(__file__).resolve().parent / registry_path.name

            with open(registry_path, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
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
