from abc import ABC, abstractmethod


class IRateLimit(ABC):
    """Abstract Base Class for endpoint rate limiting and brute force protection."""

    @abstractmethod
    def check_rate_limit(self, key: str, max_requests: int, window_seconds: int) -> bool:
        """Evaluates whether the key has exceeded the allowed request threshold within the window."""
        pass
