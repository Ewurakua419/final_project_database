# Domain exceptions for the marketplace application

class MarketplaceException(Exception):
    """Base class for all marketplace domain exceptions."""
    pass

class UserNotFoundError(MarketplaceException):
    """Raised when a user (customer or vendor) is not found."""
    pass

class InvalidCredentialsError(MarketplaceException):
    """Raised when user login authentication fails."""
    pass

class AccountSuspendedError(MarketplaceException):
    """Raised when a suspended user tries to authenticate."""
    pass

class ProductNotFoundError(MarketplaceException):
    """Raised when a product is not found in the catalog."""
    pass

class OrderNotFoundError(MarketplaceException):
    """Raised when an order is not found."""
    pass

class ReviewValidationError(MarketplaceException):
    """Raised when rating constraints or reviews fail validations."""
    pass
