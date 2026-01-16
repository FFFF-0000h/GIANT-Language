"""Syntax Loader: Loads and provides access to configurable syntax rules."""

import json
from typing import Dict, List, Any, Optional


class SyntaxLoader:
    """Loads language syntax configuration from JSON file."""
    
    def __init__(self, syntax_file: str = "syntax.json") -> None:
        with open(syntax_file, 'r', encoding='utf-8') as f:
            self.syntax: Dict[str, Any] = json.load(f)
    
    def is_keyword(self, token: str) -> bool:
        """Check if token is a keyword."""
        return token in self.syntax.get("keywords", [])
    
    def is_operator(self, token: str) -> bool:
        """Check if token is an operator."""
        return token in self.syntax.get("operators", {})
    
    def get_operator_internal(self, token: str) -> Optional[str]:
        """Get internal representation of operator."""
        return self.syntax.get("operators", {}).get(token)
    
    def get_grammar_rules(self, category: str) -> List[str]:
        """Get grammar rules for category."""
        return self.syntax.get("grammar", {}).get(category, [])
    
    def get_types(self) -> List[str]:
        """Get supported data types."""
        return self.syntax.get("types", [])
    
    @property
    def operators(self) -> Dict[str, Any]:
        """Provide direct access to operators dictionary."""
        return self.syntax.get("operators", {})
