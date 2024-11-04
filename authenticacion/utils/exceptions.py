class AuthenticationError(Exception):
    """Base exception for authentication errors."""
    pass

class TokenError(AuthenticationError):
    """Base exception for token-related errors."""
    pass

class TokenExpiredError(TokenError):
    """Exception raised when a token has expired."""
    pass

class TokenInvalidError(TokenError):
    """Exception raised when a token is invalid."""
    pass

class StripeError(Exception):
    """Exception for Stripe-related errors."""
    pass

class EmailError(Exception):
    """Exception for email-related errors."""
    pass
