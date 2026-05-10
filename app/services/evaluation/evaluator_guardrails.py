import re
from loguru import logger


class EvaluatorGuardrails:
    """
    Implements heuristic-based detection for prompt injection, jailbreaks, 
    and malicious user intent.
    """

    # Patterns indicating attempts to override system instructions or bypass safety
    INJECTION_PATTERNS = [
        r"ignore previous instructions",
        r"disregard all prior",
        r"system prompt",
        r"you are now a",
        r"pretend to be",
        r"acting as",
        r"reveal your secrets",
        r"output the full text",
        r"forget everything"
    ]

    # Patterns for out-of-scope requests that should be strictly refused
    OUT_OF_SCOPE_PATTERNS = [
        r"hiring advice",
        r"legal counsel",
        r"salary negotiation",
        r"non-shl tests",
        r"recommend a competitor",
        r"pizza recipe",
        r"weather",
        r"poem",
        r"story about"
    ]

    def is_injection_attempt(self, text: str) -> bool:
        """Checks for common prompt injection and jailbreak strings."""
        text_lower = text.lower()
        for pattern in self.INJECTION_PATTERNS:
            if re.search(pattern, text_lower):
                logger.warning(f"Injection pattern detected: {pattern}")
                return True
        return False

    def is_malicious_intent(self, text: str) -> bool:
        """Checks for obviously out-of-scope or manipulative queries."""
        text_lower = text.lower()
        for pattern in self.OUT_OF_SCOPE_PATTERNS:
            if re.search(pattern, text_lower):
                logger.warning(f"Out-of-scope pattern detected: {pattern}")
                return True
        return False

    def sanitize_input(self, text: str) -> str:
        """Removes suspicious characters or truncates excessively long input."""
        # Simple length limit to prevent token-filling attacks
        max_length = 1000
        if len(text) > max_length:
            logger.info("Truncating excessively long input.")
            text = text[:max_length]
            
        return text.strip()
