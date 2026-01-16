"""
YHWH Language - Relational Programming Exceptions
Genesis 1:1 - In the beginning...

Custom exceptions for relational programming constructs.
"""


class RelationalError(Exception):
    """Base exception for all relational programming errors."""
    pass


class AnchorError(RelationalError):
    """Raised when anchor operations fail."""
    pass


class AnchorNotFoundError(AnchorError):
    """Raised when referencing a non-existent anchor."""
    
    def __init__(self, anchor_name: str):
        self.anchor_name = anchor_name
        super().__init__(f"Anchor '{anchor_name}' not found in context")


class InvalidAnchorRangeError(AnchorError):
    """Raised when anchor range is invalid (start > end)."""
    
    def __init__(self, start: float, end: float):
        super().__init__(f"Invalid anchor range: {start} > {end}")


class RelationError(RelationalError):
    """Raised when relation operations fail."""
    pass


class IncompatibleTypesError(RelationError):
    """Raised when operations involve incompatible types."""
    
    def __init__(self, type1: type, type2: type):
        super().__init__(f"Incompatible types: {type1.__name__} and {type2.__name__}")


class ContextError(RelationalError):
    """Raised when context operations fail."""
    pass


class OptimizationError(RelationalError):
    """Raised when optimization fails."""
    pass
