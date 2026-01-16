"""Lexer: Tokenizes source code into a stream of tokens."""

import re
from typing import List, Optional
from tokens import Token, Keyword, Identifier, Integer, String, Operator, Boolean
from syntax_loader import SyntaxLoader


class Lexer:
    """Tokenizer for YHWH Language source code."""
    
    def __init__(self, text: str, syntax_loader: SyntaxLoader) -> None:
        self.text = text
        self.syntax = syntax_loader
        self.tokens: List[Token] = []
        self.pos = 0
        self.current_char: Optional[str] = self.text[0] if self.text else None
        self.tokenize()

    def advance(self) -> None:
        """Move to next character in source code."""
        self.pos += 1
        if self.pos >= len(self.text):
            self.current_char = None
        else:
            self.current_char = self.text[self.pos]

    def peek(self, offset: int = 1) -> Optional[str]:
        """Look ahead at character without advancing."""
        peek_pos = self.pos + offset
        if peek_pos >= len(self.text):
            return None
        return self.text[peek_pos]

    def skip_whitespace(self) -> None:
        """Skip whitespace characters."""
        while self.current_char and self.current_char.isspace():
            self.advance()
    
    def skip_single_line_comment(self) -> None:
        """Skip single-line comment starting with *sidegist."""
        # Already verified we're at *sidegist, skip the rest of the line
        while self.current_char and self.current_char != '\n':
            self.advance()
        if self.current_char == '\n':
            self.advance()  # Skip the newline
    
    def skip_multi_line_comment(self) -> None:
        """Skip multi-line comment between *omo* ... *omo*."""
        # Skip opening *omo*
        for _ in range(5):  # Length of "*omo*"
            self.advance()
        
        # Look for closing *omo*
        while self.current_char:
            if self.current_char == '*' and self.peek_word(5) == '*omo*':
                # Skip closing *omo*
                for _ in range(5):
                    self.advance()
                return
            self.advance()
    
    def peek_word(self, length: int) -> str:
        """Peek ahead to get a word of specific length."""
        result = ''
        for i in range(length):
            char = self.peek(i) if i == 0 else self.text[self.pos + i] if self.pos + i < len(self.text) else None
            if i == 0:
                char = self.current_char
            if char:
                result += char
            else:
                break
        return result
    
    def check_for_comments(self) -> bool:
        """Check if current position starts a comment and skip it if so."""
        # Check for *sidegist (single-line comment)
        if self.current_char == '*' and self.peek_word(9) == '*sidegist':
            self.skip_single_line_comment()
            return True
        
        # Check for *omo* (multi-line comment)
        if self.current_char == '*' and self.peek_word(5) == '*omo*':
            self.skip_multi_line_comment()
            return True
        
        return False

    def read_identifier(self) -> str:
        """Read alphanumeric identifier or keyword."""
        result = ''
        while self.current_char and (self.current_char.isalnum() or self.current_char == '_'):
            result += self.current_char
            self.advance()
        return result

    def read_string(self) -> str:
        """Read string literal enclosed in double quotes."""
        result = ''
        self.advance()  # skip opening quote
        while self.current_char and self.current_char != '"':
            result += self.current_char
            self.advance()
        self.advance()  # skip closing quote
        return result

    def read_number(self) -> str:
        result = ''
        while self.current_char and (self.current_char.isdigit() or self.current_char == '.'):
            result += self.current_char
            self.advance()
        return result
    
    def handle_at_symbol(self):
        """
        Handle @ symbol for relational constructs.
        Returns appropriate token based on what follows @.
        
        Examples:
            @anchor → Operator('@') + Keyword('anchor')
            @variable → Operator('@') + Keyword('variable')
            @optimize → Operator('@') + Keyword('optimize')
        """
        # Add @ operator token
        self.tokens.append(Operator('@'))
        self.advance()  # Skip @
        
        # Skip whitespace after @
        if self.current_char and self.current_char.isspace():
            self.skip_whitespace()
        
        # Read the relational keyword/identifier that follows
        if self.current_char and (self.current_char.isalpha() or self.current_char == '_'):
            ident = self.read_identifier()
            
            # Check if it's a known relational keyword
            relational_keywords = [
                'anchor', 'variable', 'when', 'function', 'struct', 
                'optimize', 'action', 'explain', 'explanation', 
                'priority', 'duration', 'data'
            ]
            
            if ident in relational_keywords or self.syntax.is_keyword(ident):
                self.tokens.append(Keyword(ident))
            else:
                self.tokens.append(Identifier(ident))

    def try_match_multi_word_operator(self):
        """
        Try to match multi-word operators like "divided by", "raised to", etc.
        Also handles YorubaNumeralSystem operators like "relative to", "bouncing from".
        Only checks for known multi-word operators to avoid over-consuming tokens.
        
        Returns:
            (operator_string, matched) or (None, False)
        """
        # For simplicity and correctness, check known multi-word operators
        # instead of greedily reading ahead
        
        saved_pos = self.pos
        saved_char = self.current_char
        
        # Get first word
        if not self.current_char or not (self.current_char.isalpha() or self.current_char == '_'):
            return (None, False)
        
        first_word = self.read_identifier()
        if not first_word:
            return (None, False)
        
        # Check for YorubaNumeralSystem multi-word operators first
        yns_multi_word = {
            'relative': ['to'],  # "relative to"
            'bouncing': ['from'],  # "bouncing from"
            'away': ['from'],  # "away from"
            'trending': ['toward', 'upward', 'downward'],  # "trending toward", etc.
        }
        
        if first_word in yns_multi_word:
            # Skip whitespace
            while self.current_char and self.current_char.isspace():
                self.advance()
            
            # Try to match second word
            if self.current_char and (self.current_char.isalpha() or self.current_char == '_'):
                second_word = self.read_identifier()
                
                if second_word in yns_multi_word[first_word]:
                    combined = f"{first_word} {second_word}"
                    # Map to operator value
                    operator_map = {
                        'relative to': 'relative_to',
                        'bouncing from': 'bouncing_from',
                        'away from': 'away_from',
                        'trending toward': 'trending_toward',
                        'trending upward': 'trending_upward',
                        'trending downward': 'trending_downward',
                    }
                    return (operator_map.get(combined, combined), True)
        
        # Skip whitespace
        while self.current_char and self.current_char.isspace():
            self.advance()
        
        # Try known two-word operators first
        if self.current_char and (self.current_char.isalpha() or self.current_char == '_'):
            second_word_start = self.pos
            second_word = self.read_identifier()
            two_word = first_word + ' ' + second_word
            
            if two_word in self.syntax.operators:
                return (two_word, True)
            
            # Restore to after first word
            self.pos = second_word_start
            self.current_char = self.text[self.pos] if self.pos < len(self.text) else None
            
            # Skip whitespace again
            while self.current_char and self.current_char.isspace():
                self.advance()
            
            # Try three-word operators
            if self.current_char and (self.current_char.isalpha() or self.current_char == '_'):
                third_word_start = self.pos
                third_word = self.read_identifier()
                three_word = first_word + ' ' + second_word + ' ' + third_word
                
                if three_word in self.syntax.operators:
                    return (three_word, True)
                
                # Restore to after first word for single-word check
                self.pos = second_word_start
                self.current_char = self.text[self.pos] if self.pos < len(self.text) else None
        
        # Try single-word operator
        if first_word in self.syntax.operators:
            return (first_word, True)
        
        # No match - restore completely
        self.pos = saved_pos
        self.current_char = saved_char
        return (None, False)

    def tokenize(self):
        while self.current_char:
            # Check for comments first
            if self.check_for_comments():
                continue
            
            if self.current_char.isspace():
                self.skip_whitespace()
                continue
            if self.current_char == '"':
                self.tokens.append(String(self.read_string()))
                continue
            if self.current_char.isdigit() or (self.current_char == '.' and self.peek() and self.peek().isdigit()):
                self.tokens.append(Integer(self.read_number()))
                continue
            if self.current_char.isalpha() or self.current_char == '_':
                # Try to match multi-word operators first
                operator, matched = self.try_match_multi_word_operator()
                if matched:
                    self.tokens.append(Operator(operator))
                    continue
                
                # Otherwise, treat as keyword or identifier
                ident = self.read_identifier()
                if self.syntax.is_keyword(ident):
                    self.tokens.append(Keyword(ident))
                elif ident in ['true', 'false']:
                    self.tokens.append(Boolean(ident))
                else:
                    self.tokens.append(Identifier(ident))
                continue
            
            # Check for @ symbol first (relational variable marker)
            if self.current_char == '@':
                self.handle_at_symbol()
                continue
            
            # Check for operators (multi-char first)
            op = ''
            found = False
            while self.current_char and not self.current_char.isalnum() and not self.current_char.isspace():
                op += self.current_char
                if op in self.syntax.operators:
                    self.tokens.append(Operator(op))
                    self.advance()
                    found = True
                    break
                self.advance()
            
            if not found and op:
                raise ValueError(f"Invalid operator: {op}")
        return self.tokens
