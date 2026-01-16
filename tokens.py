"""Token Definitions: Token classes for the YHWH programming language."""

from typing import Any


class Token:
    """Base token class."""
    
    def __init__(self, type: str, value: Any) -> None:
        self.type = type
        self.value = value
    
    def __repr__(self) -> str:
        return str(self.value)
    
    def lower(self) -> str:
        """Support string-like comparison."""
        if isinstance(self.value, str):
            return self.value.lower()
        return str(self.value).lower()


class Keyword(Token):
    """Language keyword token."""
    
    def __init__(self, value: str) -> None:
        super().__init__("KEYWORD", value)


class Identifier(Token):
    """Variable or function identifier token."""
    
    def __init__(self, value: str) -> None:
        super().__init__("IDENTIFIER", value)


class Integer(Token):
    """Integer literal token."""
    
    def __init__(self, value: Any) -> None:
        super().__init__("INT", int(value))


class String(Token):
    """String literal token."""
    
    def __init__(self, value: str) -> None:
        super().__init__("STRING", value)


class Operator(Token):
    """Operator token."""
    
    def __init__(self, value: str) -> None:
        super().__init__("OPERATOR", value)


class Boolean(Token):
    """Boolean literal token."""
    
    def __init__(self, value: Any) -> None:
        super().__init__("BOOL", value)
