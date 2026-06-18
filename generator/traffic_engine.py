import random
from typing import List, Dict, Optional, Type
from generator.attack_registry import AttackRegistry
from generator.traffic.base import TrafficStrategy
from generator.traffic.normal import NormalTraffic
from generator.utils.http_client import TrafficClient
from generator.utils.seed import init_seed
from generator.config import BASE_URL, MIN_REQUESTS, MAX_REQUESTS, ATTACK_PROBABILITY

class TrafficEngine:
    """
    Handles the deterministic simulation loop and traffic generation.
    
    This engine uses a student-specific seed to ensure reproducible traffic generation,
    orchestrating between normal browsing behavior and injected malicious attack vectors
    based on configured parameters.
    """
    
    def __init__(
        self, 
        student_id: str, 
        client: Optional[TrafficClient] = None,
        enabled_attacks: Optional[List[str]] = None,
        num_requests: Optional[int] = None,
        attack_count: Optional[int] = None,
        attack_ratio: Optional[float] = None,
        obfuscation_level: int = 1
    ):
        """
        Initializes the TrafficEngine.
        
        Args:
            student_id (str): Unique identifier for the student/scenario seed.
            client (TrafficClient, optional): Client instance for HTTP requests.
            enabled_attacks (List[str], optional): List of attack keys to include.
            num_requests (int, optional): Total number of requests to generate.
            attack_count (int, optional): Fixed number of attacks.
            attack_ratio (float, optional): Ratio of malicious to normal requests.
            obfuscation_level (int): Level of obfuscation (1-3) for attack payloads.
        """
        self.student_id = student_id
        self.enabled_attacks = enabled_attacks
        self.num_requests = num_requests
        self.attack_count = attack_count
        self.attack_ratio = attack_ratio
        self.obfuscation_level = obfuscation_level
        
        self.seed = init_seed(student_id)
        self.client = client or TrafficClient()
        self.normal_strategy = NormalTraffic()
        self.registry = AttackRegistry()
        self.attack_strategies = self._load_attack_strategies()

    def _load_attack_strategies(self) -> List[TrafficStrategy]:
        """
        Instantiates the enabled attack classes using the dynamic registry.
        
        Returns:
            List[TrafficStrategy]: List of initialized attack strategy objects.
        """
        target_attacks = self.enabled_attacks if self.enabled_attacks else self.registry.get_all_attack_names()
        strategies = []
        
        for name in target_attacks:
            attack_class = self.registry.get_attack_class(name)
            if attack_class:
                strategy = attack_class()
                strategy.set_obfuscation_level(self.obfuscation_level)
                strategies.append(strategy)
        
        return strategies

    def run(self, base_url: Optional[str] = None) -> Dict:
        """
        Executes the traffic generation loop based on configured strategy.
        
        This method deterministically places attacks within the generated traffic stream,
        executes requests via the HTTP client, and tracks metadata for the answer key.
        
        Args:
            base_url (str, optional): Override for the base URL. If not provided, uses `config.BASE_URL`.
            
        Returns:
            Dict: Ground truth metadata containing attack information and session details.
        """
        # Ensure determinism by seeding the global random generator at execution time
        random.seed(self.seed)
        
        target_url = base_url or BASE_URL
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
            request_kwargs, metadata = strategy.generate(target_url)
            
            if metadata:
                executed_attacks.append(metadata)
            
            self.client.execute(request_kwargs)

        return {
            "seed": str(self.seed),
            "student_id": self.student_id,
            "settings": {
                "num_requests": self.num_requests,
                "enabled_attacks": self.enabled_attacks if self.enabled_attacks is not None else list(self.registry.get_all_attack_names()),
                "attack_count": self.attack_count,
                "attack_ratio": self.attack_ratio
            },
            "total_requests": total_requests,
            "attacks": executed_attacks
        }

    def _calculate_attack_count(self, total_requests: int) -> int:
        """
        Calculates the number of attacks to inject based on provided parameters.
        
        Args:
            total_requests (int): The total number of requests planned.
            
        Returns:
            int: The calculated number of malicious requests.
        """
        if self.attack_count is not None:
            return min(total_requests, self.attack_count)
        if self.attack_ratio is not None:
            count = int(round(total_requests * self.attack_ratio))
            return max(0, min(total_requests, count))
        
        # Default probabilistic behavior (using indices for determinism)
        # Note: We simulate probability by calculating a sample size
        return int(sum(1 for _ in range(total_requests) if random.random() < ATTACK_PROBABILITY))
