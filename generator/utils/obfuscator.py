import urllib.parse

class Obfuscator:
    @staticmethod
    def url_encode(text: str) -> str:
        return urllib.parse.quote(text, safe="")
    
    @staticmethod
    def obfuscate(text: str, level: int) -> str:
        if level <= 1:
            return text
        elif level == 2:
            return Obfuscator.url_encode(text)
        elif level == 3:
            # Preserve case-sensitive commands and paths while encoding.
            return Obfuscator.url_encode(Obfuscator.url_encode(text))
        return text
