import random
from typing import List, Dict, Optional, Type
from .config import BASE_URL, MIN_REQUESTS, MAX_REQUESTS, ATTACK_PROBABILITY
from .utils.seed import init_seed
from .traffic.base import TrafficStrategy
from .traffic.normal import NormalTraffic
from .utils.http_client import TrafficClient

class TrafficEngine:
    """
    Handles the deterministic simulation loop and traffic generation.
    """
    
    # Map of attack names to their module and class names for lazy loading
    ATTACK_REGISTRY = {
        "sqli": (".attacks.sqli", "SQLIAttack"),
        "xss": (".attacks.xss", "XSSAttack"),
        "idor": (".attacks.idor", "IDORAttack"),
        "csrf": (".attacks.csrf", "CSRFAttack"),
        "rce": (".attacks.rce", "RCEAttack"),
        "lfi": (".attacks.lfi", "LFIAttack"),
        "cmdi": (".attacks.cmdi", "CMDIAttack")
    }

    def __init__(
        self, 
        student_id: str, 
        client: Optional[TrafficClient] = None,
        enabled_attacks: Optional[List[str]] = None,
        num_requests: Optional[int] = None,
        attack_count: Optional[int] = None,
        attack_ratio: Optional[float] = None
    ):
        self.student_id = student_id
        self.enabled_attacks = enabled_attacks
        self.num_requests = num_requests
        self.attack_count = attack_count
        self.attack_ratio = attack_ratio
        
        self.seed = init_seed(student_id)
        self.client = client or TrafficClient()
        self.normal_strategy = NormalTraffic()
        self.attack_strategies = self._load_attack_strategies()

    def _load_attack_strategies(self) -> List[TrafficStrategy]:
        """Instantiates the enabled attack classes using lazy loading."""
        import importlib
        
        target_attacks = self.enabled_attacks if self.enabled_attacks else self.ATTACK_REGISTRY.keys()
        strategies = []
        
        for name in target_attacks:
            if name in self.ATTACK_REGISTRY:
                module_path, class_name = self.ATTACK_REGISTRY[name]
                try:
                    module = importlib.import_module(module_path, package="generator")
                    attack_class = getattr(module, class_name)
                    strategies.append(attack_class())
                except (ImportError, AttributeError) as e:
                    print(f"Warning: Could not load attack {name}: {e}")
        
        return strategies

    def run(self) -> Dict:
        """
        Executes the traffic generation loop.
        Returns the data for the answer key.
        """
        total_requests = self.num_requests if self.num_requests is not None else random.randint(MIN_REQUESTS, MAX_REQUESTS)
        
        # Calculate final attack count
        final_attack_count = self._calculate_attack_count(total_requests)
        
        # Pre-calculate attack indices for deterministic placement
        attack_indices = set()
        if final_attack_count > 0 and self.attack_strategies:
            attack_indices = set(random.sample(range(total_requests), final_attack_count))

        executed_attacks = []

        for i in range(total_requests):
            # Polymorphic Strategy Selection
            if i in attack_indices:
                strategy = random.choice(self.attack_strategies)
            else:
                strategy = self.normal_strategy
            
            # Generate and Execute
            request_kwargs, metadata = strategy.generate(BASE_URL)
            
            if metadata:
                executed_attacks.append(metadata)
            
            self.client.execute(request_kwargs)

        return {
            "seed": str(self.seed),
            "student_id": self.student_id,
            "settings": {
                "num_requests": self.num_requests,
                "enabled_attacks": self.enabled_attacks if self.enabled_attacks is not None else list(self.ATTACK_REGISTRY.keys()),
                "attack_count": self.attack_count,
                "attack_ratio": self.attack_ratio
            },
            "total_requests": total_requests,
            "attacks": executed_attacks
        }

    def _calculate_attack_count(self, total_requests: int) -> int:
        if self.attack_count is not None:
            return min(total_requests, self.attack_count)
        if self.attack_ratio is not None:
            count = int(round(total_requests * self.attack_ratio))
            return max(0, min(total_requests, count))
        
        # Default probabilistic behavior (using indices for determinism)
        # Note: We simulate probability by calculating a sample size
        return int(sum(1 for _ in range(total_requests) if random.random() < ATTACK_PROBABILITY))
