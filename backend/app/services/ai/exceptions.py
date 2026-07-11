class AIError(Exception):
    """Base exception for the AI platform."""
    def __init__(self, message: str, original_error: Exception = None) -> None:
        self.message = message
        self.original_error = original_error
        super().__init__(message)


class AuthenticationError(AIError):
    """Raised when authentication fails (e.g. invalid API key)."""
    pass


class ProviderUnavailableError(AIError):
    """Raised when the provider endpoint is down or unreachable."""
    pass


class GenerationError(AIError):
    """Raised when content generation fails."""
    pass


class RateLimitError(AIError):
    """Raised when rate limits are exceeded."""
    pass


class TimeoutError(AIError):
    """Raised when a request to the AI provider times out."""
    pass


class ConfigurationError(AIError):
    """Raised when provider configuration is invalid or missing."""
    pass
