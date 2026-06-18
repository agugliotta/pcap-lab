import random
import urllib.parse

class Obfuscator:
    @staticmethod
    def url_encode(text: str) -> str:
        return urllib.parse.quote(text)
    
    @staticmethod
    def random_caps(text: str) -> str:
        return "".join(c.upper() if random.random() > 0.5 else c.lower() for c in text)
    
    @staticmethod
    def obfuscate(text: str, level: int) -> str:
        if level <= 1:
            return text
        elif level == 2:
            return Obfuscator.url_encode(Obfuscator.random_caps(text))
        elif level == 3:
            # Advanced obfuscation: Double URL encoding + random capitalization
            return Obfuscator.url_encode(Obfuscator.url_encode(Obfuscator.random_caps(text)))
        return text
