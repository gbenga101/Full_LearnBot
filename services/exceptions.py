# services/exceptions.py

class ProviderError(Exception):
    """Base provider error."""

class RateLimitError(ProviderError):
    """Raised when provider returns 429 / rate limited."""

class APIError(ProviderError):
    """Raised for HTTP 4xx/5xx or unexpected provider responses."""

class NetworkError(ProviderError):
    """Raised for network/requests exceptions and timeouts."""
    
class ConfigurationError(ProviderError):
    """Raised for configuration issues, e.g., missing API key."""