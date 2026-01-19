"""Parser: Recursive descent parser building AST from tokens.

Handles Pidgin English syntax + YorubaNumeralSystem relational programming.
"""

from typing import Optional

from tokens import Token, Keyword, Identifier, Integer, String, Operator, Boolean
from relational.ast_nodes import (
    AnchorDeclaration, RelationalVariable, WhenStatement, OptimizationDirective,
    AnchorType, AnchorProperty, RelativeToClause, RelationalExpression,
    IsExpression, ActionStatement, ActionBlock, NumberLiteral, StringLiteral, BooleanLiteral,
    Assign, Var, Num, Str, Bool, BinOp, UnaryOp, If, While, Print, Block,
    FunctionDef, FunctionCall, TryCatch, ListAnchors, DescribeAnchor
)
from syntax_loader import SyntaxLoader
from math_operations import MathOperations

class Parser:
    """
    Recursive descent parser for GIANT Language (Nigerian Pidgin + YorubaNumeralSystem).
    
    Builds AST from token stream with support for:
    - Variable assignments (make/set syntax)
    - Formal declarations (let...be syntax)
    - Mathematical expressions with proper precedence
    - Multi-word operators (divided by, square root of, etc.)
    - Relational programming constructs (@anchor, when, relational variables)
    """

    def __init__(self, syntax_loader: SyntaxLoader) -> None:
        """Initialize parser with syntax loader.
        
        Args:
            syntax_loader: Configured syntax loader instance
        """
        self.syntax = syntax_loader
        self.tokens: list[Token] = []
        self.current: int = 0

    def parse(self, tokens: list[Token]) -> Block:
        """Parse a list of tokens and return AST.
        
        Args:
            tokens: List of tokens from lexer
            
        Returns:
            Block node containing all statements
        """
        self.tokens = tokens
        self.current = 0
        return self.parse_program()

    def parse_program(self):
        """program: statement*"""
        statements = []
        while not self.is_at_end():
            stmt = self.parse_statement()
            if stmt:
                statements.append(stmt)
        return Block(statements)

    def parse_statement(self):
        """Parse a single statement"""
        token = self.peek()
        
        # Check for relational syntax first
        if token and isinstance(token, Operator) and token.value == '@':
            # Peek ahead to determine which type
            saved_pos = self.current
            self.advance()  # Skip @
            next_token = self.peek()
            self.current = saved_pos  # Restore position
            
            if next_token and isinstance(next_token, Keyword):
                kw = next_token.value.lower()
                if kw == 'anchor':
                    return self.parse_anchor_declaration()
                elif kw == 'optimize':
                    return self.parse_optimization_directive()
        
        # Check for keyword-based statements
        if token and isinstance(token, Keyword):
            keyword_val = token.value.lower()
            
            # Check for anchor management commands
            if keyword_val == 'list':
                # Check for "list anchors"
                next_token = self.peek_ahead(1)
                if next_token and isinstance(next_token, Keyword) and next_token.value.lower() in ['anchor', 'anchors']:
                    return self.parse_list_anchors()
            
            if keyword_val in ['describe', 'inspect']:
                # Check for "describe anchor NAME"
                next_token = self.peek_ahead(1)
                if next_token and isinstance(next_token, Keyword) and next_token.value.lower() == 'anchor':
                    return self.parse_describe_anchor()
            
            if keyword_val == 'show':
                # Could be "show anchor NAME" or regular "show var"
                next_token = self.peek_ahead(1)
                if next_token and isinstance(next_token, Keyword) and next_token.value.lower() == 'anchor':
                    return self.parse_describe_anchor()
                # Otherwise fall through to output parsing
            
            # Check for relational keywords
            if keyword_val == 'when':
                return self.parse_when_statement()
            
            if keyword_val == 'relational':
                return self.parse_relational_variable()
            
            # Check for formal declarations (let x be...)
            if keyword_val == 'let':
                return self.parse_formal_declaration()
            
            # Check for make assignments (make x be...)
            if keyword_val == 'make':
                return self.parse_make_assignment()
            
            # Check for set assignments (set x to...)
            if keyword_val == 'set':
                return self.parse_set_assignment()
            
            # Check for output statements (talk, show, wetin)
            if keyword_val in ['talk', 'show', 'wetin']:
                return self.parse_output()
        
        # Try to parse as expression
        expr = self.parse_expression()
        if expr:
            return expr
        
        return None

    def parse_formal_declaration(self):
        """
        Parse formal declaration: 
        - let IDENTIFIER be expr
        - let IDENTIFIER be equal to expr
        """
        self.consume(Keyword, "Expected 'let'")
        var_name = self.consume(Identifier, "Expected variable name").value
        
        # Consume 'be' keyword
        be_token = self.peek()
        if isinstance(be_token, Keyword) and be_token.value.lower() == 'be':
            self.advance()
        else:
            raise SyntaxError("Expected 'be' in formal declaration")
        
        # Check for optional 'equal to'
        next_token = self.peek()
        if next_token and ((isinstance(next_token, Keyword) or isinstance(next_token, Operator)) and 
            next_token.value.lower() == 'equal'):
            self.advance()  # consume 'equal'
            if (self.peek() and isinstance(self.peek(), Keyword) and 
                self.peek().value.lower() == 'to'):
                self.advance()  # consume 'to'
        
        # Now parse the expression
        expr = self.parse_expression()
        return Assign(var_name, expr)

    def parse_make_assignment(self):
        """Parse: make IDENTIFIER be expr"""
        self.consume(Keyword, "Expected 'make'")
        var_name = self.consume(Identifier, "Expected variable name").value
        
        be_token = self.peek()
        if be_token and isinstance(be_token, Keyword) and be_token.value.lower() == 'be':
            self.advance()
        else:
            raise SyntaxError("Expected 'be' after variable name in 'make' statement")
        
        expr = self.parse_expression()
        return Assign(var_name, expr)

    def parse_set_assignment(self):
        """Parse: set IDENTIFIER to expr"""
        self.consume(Keyword, "Expected 'set'")
        var_name = self.consume(Identifier, "Expected variable name").value
        
        to_token = self.peek()
        if to_token and isinstance(to_token, Keyword) and to_token.value.lower() == 'to':
            self.advance()
        else:
            raise SyntaxError("Expected 'to' after variable name in 'set' statement")
        
        expr = self.parse_expression()
        return Assign(var_name, expr)

    def parse_output(self):
        """Parse output statements: talk expr, show var, wetin be var"""
        token = self.peek()
        if isinstance(token, Keyword):
            keyword = token.value.lower()
            self.advance()
            
            if keyword == 'talk':
                expr = self.parse_expression()
                return Print(expr)
            elif keyword == 'show':
                var_token = self.consume(Identifier, "Expected variable name")
                return Print(Var(var_token.value))
            elif keyword == 'wetin':
                # wetin be var?
                if self.peek() and isinstance(self.peek(), Keyword) and self.peek().value.lower() == 'be':
                    self.advance()
                var_token = self.consume(Identifier, "Expected variable name")
                return Print(Var(var_token.value))
        
        raise SyntaxError("Invalid output statement")

    def parse_expression(self):
        """Parse expression with proper precedence"""
        return self.parse_additive()

    def parse_additive(self):
        """Parse addition/subtraction (lowest precedence)"""
        expr = self.parse_multiplicative()
        
        while self.peek() and isinstance(self.peek(), Operator):
            op_token = self.peek()
            op_str = op_token.value.lower()
            canonical, valid = MathOperations.normalize_operator(op_str)
            
            # Check if it's an additive operator
            if canonical in ['plus', 'minus']:
                self.advance()
                right = self.parse_multiplicative()
                expr = BinOp(expr, op_str, right)
            else:
                break
        
        return expr

    def parse_multiplicative(self):
        """Parse multiplication/division (medium precedence)"""
        expr = self.parse_power()
        
        while self.peek() and isinstance(self.peek(), Operator):
            op_token = self.peek()
            op_str = op_token.value.lower()
            canonical, valid = MathOperations.normalize_operator(op_str)
            
            # Check if it's a multiplicative operator
            if canonical in ['times', 'divided_by']:
                self.advance()
                right = self.parse_power()
                expr = BinOp(expr, op_str, right)
            else:
                break
        
        return expr

    def parse_power(self):
        """Parse power operations (high precedence)"""
        expr = self.parse_unary()
        
        if self.peek() and isinstance(self.peek(), Operator):
            op_token = self.peek()
            op_str = op_token.value.lower()
            canonical, valid = MathOperations.normalize_operator(op_str)
            
            if canonical in ['power', 'sqrt', 'cbrt']:
                self.advance()
                right = self.parse_unary()
                expr = BinOp(expr, op_str, right)
        
        return expr

    def parse_unary(self):
        """Parse unary operations: square root of x, cube root of x"""
        token = self.peek()
        
        # Check for multi-word operators like "square root of" (lexed as single operator)
        if token and isinstance(token, Operator):
            op_value = token.value.lower()
            
            # Check if it's "square root" operator
            if op_value == 'square root':
                self.advance()
                # Check for "of" keyword
                if self.peek() and isinstance(self.peek(), Operator) and self.peek().value.lower() == 'of':
                    self.advance()
                operand = self.parse_primary()
                return UnaryOp('sqrt', operand)
            
            # Check if it's "cube root" operator
            elif op_value == 'cube root':
                self.advance()
                # Check for "of" keyword
                if self.peek() and isinstance(self.peek(), Operator) and self.peek().value.lower() == 'of':
                    self.advance()
                operand = self.parse_primary()
                return UnaryOp('cbrt', operand)
        
        return self.parse_primary()

    def parse_primary(self):
        """Parse primary values: numbers, strings, variables, parenthesized expressions"""
        token = self.peek()
        
        if not token:
            raise SyntaxError("Unexpected end of input")
        
        # Numbers
        if isinstance(token, Integer):
            self.advance()
            return Num(token.value)
        
        # Strings
        if isinstance(token, String):
            self.advance()
            return Str(token.value)
        
        # Booleans
        if isinstance(token, Boolean):
            self.advance()
            return Bool(token.value.lower() == 'true')
        
        # Variables
        if isinstance(token, Identifier):
            self.advance()
            return Var(token.value)
        
        raise SyntaxError(f"Unexpected token: {token}")

    # ========================================================================
    # RELATIONAL/YorubaNumeralSystem PARSING METHODS
    # ========================================================================
    
    def parse_anchor_declaration(self) -> AnchorDeclaration:
        """
        Parse @anchor declarations supporting two syntaxes:
        
        1. Simple style: @anchor name = value property1 = val1 property2 = val2
        2. YorubaNumeralSystem style: @anchor(name="name", value=100, property1=val1)
        """
        # Consume @ operator
        at_token = self.peek()
        if not (isinstance(at_token, Operator) and at_token.value == '@'):
            raise SyntaxError("Expected '@' for anchor declaration")
        self.advance()
        
        # Consume 'anchor' keyword
        anchor_token = self.peek()
        if not (isinstance(anchor_token, Keyword) and anchor_token.value.lower() == 'anchor'):
            raise SyntaxError("Expected 'anchor' keyword after '@'")
        self.advance()
        
        # Check for YorubaNumeralSystem style (parentheses) vs simple style
        next_token = self.peek()
        if isinstance(next_token, Operator) and next_token.value == '(':
            return self._parse_anchor_yns_style()
        else:
            return self._parse_anchor_simple_style()
    
    def _parse_anchor_simple_style(self) -> AnchorDeclaration:
        """Parse simple style: @anchor name = value prop1 = val1"""
        # Get anchor name
        name_token = self.consume(Identifier, "Expected anchor name")
        name = name_token.value
        
        # Consume '='
        eq_token = self.peek()
        if not (isinstance(eq_token, Operator) and eq_token.value in ['=', 'na']):
            raise SyntaxError("Expected '=' after anchor name")
        self.advance()
        
        # Parse anchor value
        value = self.parse_expression()
        
        # Convert to literals
        if isinstance(value, Num):
            value = NumberLiteral(value=value.value)
        elif isinstance(value, Str):
            value = StringLiteral(value=value.value)
        elif isinstance(value, Bool):
            value = BooleanLiteral(value=value.value)
        
        # Parse optional properties
        properties = []
        while (self.peek() and isinstance(self.peek(), Identifier) and 
               not isinstance(self.peek(), Keyword)):
            prop_name = self.consume(Identifier, "Expected property name").value
            
            eq = self.peek()
            if not (isinstance(eq, Operator) and eq.value == '='):
                break
            self.advance()
            
            prop_value = self.parse_expression()
            
            # Convert to literals
            if isinstance(prop_value, Num):
                prop_value = NumberLiteral(value=prop_value.value)
            elif isinstance(prop_value, Str):
                prop_value = StringLiteral(value=prop_value.value)
            elif isinstance(prop_value, Bool):
                prop_value = BooleanLiteral(value=prop_value.value)
            
            properties.append(AnchorProperty(key=prop_name, value=prop_value))
        
        return AnchorDeclaration(
            name=name,
            anchor_type=AnchorType.STATIC,
            value=value,
            properties=properties or []
        )
    
    def _parse_anchor_yns_style(self) -> AnchorDeclaration:
        """Parse YorubaNumeralSystem style: @anchor(name="name", value=100, tolerance=5)"""
        # Consume opening parenthesis
        self.consume(Operator, "Expected '(' for YorubaNumeralSystem anchor style")
        
        # Parse name=value pairs separated by commas
        name = None
        value = None
        properties = []
        
        while self.peek() and not (isinstance(self.peek(), Operator) and self.peek().value == ')'):
            # Parse property name
            prop_name_token = self.consume(Identifier, "Expected property name")
            prop_name = prop_name_token.value
            
            # Consume '='
            self.consume(Operator, "Expected '=' after property name")
            
            # Parse property value
            prop_value = self.parse_expression()
            
            # Convert to literals
            if isinstance(prop_value, Num):
                prop_value = NumberLiteral(value=prop_value.value)
            elif isinstance(prop_value, Str):
                prop_value = StringLiteral(value=prop_value.value)
            elif isinstance(prop_value, Bool):
                prop_value = BooleanLiteral(value=prop_value.value)
            
            # Special handling for name and value parameters
            if prop_name == "name":
                if isinstance(prop_value, StringLiteral):
                    name = prop_value.value
                else:
                    raise SyntaxError("Anchor name must be a string in YorubaNumeralSystem style")
            elif prop_name == "value":
                value = prop_value
            else:
                # Map common YorubaNumeralSystem names to internal names
                if prop_name == "significance":
                    prop_name = "description"
                properties.append(AnchorProperty(key=prop_name, value=prop_value))
            
            # Check for comma
            if self.peek() and isinstance(self.peek(), Operator) and self.peek().value == ',':
                self.advance()
        
        # Consume closing parenthesis
        self.consume(Operator, "Expected ')' to close YorubaNumeralSystem anchor")
        
        if name is None:
            raise SyntaxError("YorubaNumeralSystem anchor must have 'name' parameter")
        if value is None:
            raise SyntaxError("YorubaNumeralSystem anchor must have 'value' parameter")
        
        return AnchorDeclaration(
            name=name,
            anchor_type=AnchorType.STATIC,
            value=value,
            properties=properties
        )
    
    def parse_relational_variable(self) -> RelationalVariable:
        """
        Parse relational variable declarations from YorubaNumeralSystem.
        
        Syntax: relational var = value relative to [anchors]
        Example: relational temp = 78 relative to [optimal, danger]
        """
        # 'relational' keyword
        self.advance()
        
        # Get variable name
        name_token = self.consume(Identifier, "Expected variable name")
        name = name_token.value
        
        # Consume '='
        eq_token = self.peek()
        if not (isinstance(eq_token, Operator) and eq_token.value == '='):
            raise SyntaxError("Expected '=' after variable name")
        self.advance()
        
        # Parse value
        value = self.parse_expression()
        
        # Parse optional "relative to" clause
        # Can be either: Keyword('relative') + Keyword('to')
        #           or:  Operator('relative_to')
        relative_to_clause = None
        next_token = self.peek()
        
        if next_token:
            # Check for Operator('relative_to')
            if isinstance(next_token, Operator) and next_token.value == 'relative_to':
                self.advance()  # Consume relative_to
            # Or check for Keyword('relative') + Keyword('to')
            elif isinstance(next_token, Keyword) and next_token.value.lower() == 'relative':
                self.advance()  # Consume 'relative'
                to_token = self.peek()
                if not (isinstance(to_token, Keyword) and to_token.value.lower() == 'to'):
                    raise SyntaxError("Expected 'to' after 'relative'")
                self.advance()  # Consume 'to'
            else:
                # No relative_to clause
                return RelationalVariable(
                    name=name,
                    value=value,
                    relative_to=None
                )
            
            # Parse anchor list [anchor1, anchor2]
            bracket_open = self.peek()
            if not (isinstance(bracket_open, Operator) and bracket_open.value == '['):
                raise SyntaxError("Expected '[' to start anchor list")
            self.advance()
            
            # Parse anchor names
            anchors = []
            while True:
                anchor_name = self.consume(Identifier, "Expected anchor name").value
                anchors.append(anchor_name)
                
                next_token = self.peek()
                if isinstance(next_token, Operator) and next_token.value == ',':
                    self.advance()
                    continue
                elif isinstance(next_token, Operator) and next_token.value == ']':
                    self.advance()
                    break
                else:
                    raise SyntaxError("Expected ',' or ']' in anchor list")
            
            relative_to_clause = RelativeToClause(anchors=anchors)
        
        # Parse optional properties (context, policy, confidence, etc.)
        properties = {}
        while self.peek():
            next_token = self.peek()
            
            # Accept both Identifier and Keyword for property names
            # (keywords like 'context', 'confidence', 'policy' can be property names)
            if isinstance(next_token, (Identifier, Keyword)):
                # Check if it's a statement keyword (not a property)
                if isinstance(next_token, Keyword) and next_token.value.lower() in [
                    'talk', 'relational', 'when', 'list', 'describe', 
                    'anchor', 'suppose', 'den', 'make', 'repeat', 'stop'
                ]:
                    break  # Start of next statement
                
                # Consume the property name
                self.advance()
                prop_name = next_token.value
                
                # Check for '=' after property name
                eq = self.peek()
                if not (isinstance(eq, Operator) and eq.value == '='):
                    # Not a property assignment
                    break
                self.advance()  # Consume '='
                
                prop_value = self.parse_expression()
                
                # Convert to literals
                if isinstance(prop_value, Num):
                    prop_value = NumberLiteral(value=prop_value.value)
                elif isinstance(prop_value, Str):
                    prop_value = StringLiteral(value=prop_value.value)
                elif isinstance(prop_value, Bool):
                    prop_value = BooleanLiteral(value=prop_value.value)
                
                properties[prop_name] = prop_value
            else:
                break
        
        return RelationalVariable(
            name=name,
            value=value,
            relative_to=relative_to_clause,
            properties=properties
        )
    
    def parse_when_statement(self) -> WhenStatement:
        """
        Parse when-clauses from YorubaNumeralSystem.
        
        Syntax: when condition: @action statement
        Example: when temp is "over" optimal: @action alert()
        """
        # 'when' keyword
        self.advance()
        
        # Parse condition
        condition = self.parse_relational_expression()
        
        # Consume ':'
        colon_token = self.peek()
        if not (isinstance(colon_token, Operator) and colon_token.value == ':'):
            raise SyntaxError("Expected ':' after when condition")
        self.advance()
        
        # Parse action block (simplified)
        actions = []
        
        # If next is @action, parse it
        if (self.peek() and isinstance(self.peek(), Operator) and 
            self.peek().value == '@'):
            self.advance()  # Skip @
            
            action_kw = self.peek()
            if isinstance(action_kw, Keyword) and action_kw.value.lower() == 'action':
                self.advance()  # Skip 'action'
                
                # Parse the action statement
                action_stmt = self.parse_statement()
                if action_stmt:
                    actions.append(ActionStatement(action=action_stmt))
        
        action_block = ActionBlock(actions=actions, metadata={})
        
        return WhenStatement(
            condition=condition,
            action_block=action_block
        )
    
    def parse_relational_expression(self) -> RelationalExpression:
        """
        Parse relational expressions from YorubaNumeralSystem.
        
        Supports: is, approaches, enters, leaves, crosses
        Example: temp is "over" optimal
        """
        left = self.parse_expression()
        
        op_token = self.peek()
        if isinstance(op_token, Keyword):
            op = op_token.value.lower()
            
            if op == 'is':
                self.advance()
                
                # Parse qualifier ("over", "under", etc.)
                qualifier = ""
                rel_token = self.peek()
                if isinstance(rel_token, String):
                    qualifier = rel_token.value
                    self.advance()
                
                # Parse anchor reference
                anchor_ref = self.consume(Identifier, "Expected anchor name").value
                
                return IsExpression(
                    left=left,
                    qualifier=qualifier,
                    right=Var(anchor_ref)
                )
            
            elif op in ['approaches', 'enters', 'leaves', 'crosses']:
                self.advance()
                threshold = self.parse_expression()
                
                return RelationalExpression(
                    left=left,
                    operator=op,
                    right=threshold
                )
        
        # Fallback
        return RelationalExpression(
            left=left,
            operator="",
            right=None
        )
    
    def parse_optimization_directive(self) -> OptimizationDirective:
        """
        Parse @optimize directives from YorubaNumeralSystem.
        
        Syntax: @optimize for: - objective: minimize/maximize
        Example: @optimize for: - energy: minimize - comfort: maximize
        """
        # Consume @ operator
        at_token = self.peek()
        if not (isinstance(at_token, Operator) and at_token.value == '@'):
            raise SyntaxError("Expected '@' for optimization directive")
        self.advance()
        
        # Consume 'optimize' keyword
        opt_token = self.peek()
        if not (isinstance(opt_token, Keyword) and opt_token.value.lower() == 'optimize'):
            raise SyntaxError("Expected 'optimize' keyword after '@'")
        self.advance()
        
        # Consume 'for'
        for_token = self.peek()
        if not (isinstance(for_token, Keyword) and for_token.value.lower() == 'for'):
            raise SyntaxError("Expected 'for' after 'optimize'")
        self.advance()
        
        # Consume ':'
        colon_token = self.peek()
        if not (isinstance(colon_token, Operator) and colon_token.value == ':'):
            raise SyntaxError("Expected ':' after 'for'")
        self.advance()
        
        # For simplicity, return basic directive
        return OptimizationDirective(
            objectives=[],
            constraints=[]
        )

    # ========================================================================
    # ANCHOR MANAGEMENT PARSING
    # ========================================================================
    
    def parse_list_anchors(self) -> ListAnchors:
        """
        Parse 'list anchors' command.
        
        Syntax: list anchors
        """
        self.consume(Keyword, "Expected 'list'")  # Consume 'list'
        self.consume(Keyword, "Expected 'anchor' or 'anchors'")  # Consume 'anchor(s)'
        return ListAnchors()
    
    def parse_describe_anchor(self) -> DescribeAnchor:
        """
        Parse 'describe anchor NAME' or 'show anchor NAME' command.
        
        Syntax: describe anchor NAME
                show anchor NAME
                inspect anchor NAME
        """
        self.consume(Keyword, "Expected command keyword")  # Consume 'describe'/'show'/'inspect'
        self.consume(Keyword, "Expected 'anchor'")  # Consume 'anchor'
        anchor_name = self.consume(Identifier, "Expected anchor name").value
        return DescribeAnchor(anchor_name)

    # ========================================================================
    # HELPER METHODS
    # ========================================================================
    
    def peek(self):
        """Get current token without advancing"""
        if self.is_at_end():
            return None
        return self.tokens[self.current]
    
    def peek_ahead(self, offset):
        """Peek ahead by offset tokens"""
        pos = self.current + offset
        if pos >= len(self.tokens):
            return None
        return self.tokens[pos]

    def advance(self):
        """Consume current token and move to next"""
        if not self.is_at_end():
            self.current += 1

    def is_at_end(self):
        """Check if we've reached end of tokens"""
        return self.current >= len(self.tokens)

    def consume(self, token_type, message):
        """Consume a token of expected type or raise error"""
        token = self.peek()
        if not token or not isinstance(token, token_type):
            raise SyntaxError(message)
        self.advance()
        return token
