import random
import hashlib

def init_seed(student_id: str):
    """
    Initialize the random seed based on the student identifier.
    Uses SHA256 to ensure a uniform distribution from the input string.
    """
    # Create a deterministic hash of the student ID
    hash_object = hashlib.sha256(student_id.encode())
    # Convert the hash to an integer seed
    seed_int = int(hash_object.hexdigest(), 16)
    # Seed the random number generator
    random.seed(seed_int)
    return seed_int
