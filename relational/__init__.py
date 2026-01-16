"""
YHWH Language - Relational Programming Integration Layer

This module provides the integration layer between the existing Pidgin syntax
and the new relational programming paradigm. It extends the language with:

- Anchors: Meaningful reference points for values
- Relations: Values that understand their position in a landscape
- When-clauses: Context-aware conditional logic
- Optimization: Multi-objective decision making

Architecture:
    relational/
    ├── ast_nodes.py              # Extended AST nodes
    ├── parser_extensions.py      # Parser for relational syntax
    ├── interpreter_extensions.py # Interpreter for relational nodes
    └── __init__.py              # This file (public API)

Usage:
    # Import AST nodes
    from relational import (
        AnchorDeclaration, RelationalVariable, WhenStatement,
        AnchorType, RelationalExpression
    )
    
    # Import parser extensions (Phase 2B)
    from relational import RelationalParser
    
    # Import interpreter extensions (Phase 2C)
    from relational import RelationalInterpreter

Integration with Core:
    The relational module bridges between:
    - Language syntax (AST nodes defined here)
    - Runtime semantics (core/ module with Anchor, Relation, Context, Optimizer)
    
    Flow:
        Source Code → Lexer → Parser → AST → Interpreter → Core Runtime

Example:
    # In .naija file:
    @anchor optimal_temp = 75.0
        unit = "celsius"
        tolerance = 5.0
    
    relational reactor_temp = 92.7 relative_to [optimal_temp]
    
    when reactor_temp is "over" optimal_temp:
        action increase_cooling()
"""

# ============================================================================
# AST NODES (Complete - Phase 2A)
# ============================================================================

from .ast_nodes import (
    # Base classes
    Node,
    Expression,
    Statement,
    
    # Literals
    NumberLiteral,
    StringLiteral,
    BooleanLiteral,
    
    # Pidgin syntax nodes (legacy compatibility)
    BinOp,
    UnaryOp,
    Assign,
    Var,
    Num,
    Str,
    Bool,
    If,
    While,
    Print,
    FunctionDef,
    FunctionCall,
    TryCatch,
    Block,
    PidginVariable,
    PidginPrint,
    PidginBinaryOp,
    PidginUnaryOp,
    
    # Relational syntax nodes
    AnchorType,
    AnchorProperty,
    AnchorDeclaration,
    RelativeToClause,
    AnchorReference,
    RelationalVariable,
    RelationalExpression,
    RangeExpression,
    WhenStatement,
    ActionBlock,
    ActionStatement,
    FunctionDeclaration,
    Parameter,
    TypeSpecification,
    OptimizationDirective,
    
    # Specialized relational operators
    IsExpression,
    ApproachesExpression,
    EntersExpression,
    LeavesExpression,
    
    # Compound expressions
    LogicalExpression,
    WithProperties,
    
    # Visitor pattern
    NodeVisitor,
    NodeTransformer,
    
    # Utilities
    convert_legacy_to_modern,
    is_relational_node,
    extract_anchors,
    extract_relational_variables,
)

# ============================================================================
# VERSION INFO
# ============================================================================

__version__ = '0.1.0'
__author__ = 'YHWH Language Team'
__status__ = 'Phase 2A Complete - AST Nodes'

# ============================================================================
# PUBLIC API
# ============================================================================

__all__ = [
    # Core types
    'Node', 'Expression', 'Statement',
    
    # Literals
    'NumberLiteral', 'StringLiteral', 'BooleanLiteral',
    
    # Pidgin syntax
    'PidginVariable', 'PidginPrint', 'PidginBinaryOp', 'PidginUnaryOp',
    
    # Relational types
    'AnchorType',
    
    # Relational declarations
    'AnchorProperty', 'AnchorDeclaration',
    'RelativeToClause', 'AnchorReference', 'RelationalVariable',
    
    # Relational expressions
    'RelationalExpression', 'RangeExpression',
    'IsExpression', 'ApproachesExpression', 'EntersExpression', 'LeavesExpression',
    
    # Control flow
    'WhenStatement', 'ActionBlock', 'ActionStatement',
    
    # Functions and types
    'FunctionDeclaration', 'Parameter', 'TypeSpecification',
    
    # Structures
    'Block', 'OptimizationDirective',
    
    # Compound
    'LogicalExpression', 'WithProperties',
    
    # Visitors
    'NodeVisitor', 'NodeTransformer',
    
    # Utilities
    'convert_legacy_to_modern', 'is_relational_node',
    'extract_anchors', 'extract_relational_variables',
]
