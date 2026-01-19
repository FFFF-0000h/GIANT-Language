"""
Abstract Syntax Tree nodes for GIANT Language with relational extensions

This module contains ALL AST nodes for the GIANT Language:
- Legacy Pidgin nodes (BinOp, Assign, Print, etc.)
- Relational extensions (Anchors, Relations, When-clauses)
- Optimization directives for multi-objective decision making

Design Principles:
- Single source of truth for all AST nodes
- Type-safe with full type annotations
- Self-validating with rich error messages
- Visitor pattern support for traversal
- Pretty-printable for debugging

Integration:
    from relational.ast_nodes import AnchorDeclaration, RelationalVariable, Assign
    
    anchor = AnchorDeclaration(
        name="optimal_temp",
        anchor_type=AnchorType.STATIC,
        value=NumberLiteral(75.0)
    )
"""

from typing import List, Dict, Any, Optional, Union, Callable
from dataclasses import dataclass, field
from enum import Enum

# ============================================================================
# BASE NODES - Shared between legacy and modern
# ============================================================================

class ASTNode:
    """Legacy base class for backward compatibility"""
    pass


@dataclass
class Node(ASTNode):
    """
    Base class for all modern AST nodes with location tracking.
    
    Attributes:
        lineno: Line number in source file (1-indexed)
        col_offset: Column offset in source line (0-indexed)
    """
    lineno: int = 0
    col_offset: int = 0
    
    def __post_init__(self):
        """Validate node after initialization"""
        self.validate()
    
    def validate(self) -> None:
        """Override to add node-specific validation"""
        pass
    
    def accept(self, visitor: 'NodeVisitor') -> Any:
        """Visitor pattern support"""
        method_name = f'visit_{self.__class__.__name__}'
        visitor_method = getattr(visitor, method_name, visitor.generic_visit)
        return visitor_method(self)


# ============================================================================
# LEGACY PIDGIN NODES - For backward compatibility
# ============================================================================

class BinOp(ASTNode):
    """Binary operation (legacy)"""
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right
    
    def __repr__(self):
        return f"BinOp({self.left} {self.op} {self.right})"


class UnaryOp(ASTNode):
    """Unary operation (legacy)"""
    def __init__(self, op, operand):
        self.op = op
        self.operand = operand
    
    def __repr__(self):
        return f"UnaryOp({self.op} {self.operand})"


class Assign(ASTNode):
    """Variable assignment (legacy)"""
    def __init__(self, var, expr):
        self.var = var
        self.expr = expr
    
    def __repr__(self):
        return f"Assign({self.var} = {self.expr})"


class Var(ASTNode):
    """Variable reference (legacy) - treated as Expression for compatibility"""
    def __init__(self, name):
        self.name = name
    
    def __repr__(self):
        return f"Var({self.name})"


class Num(ASTNode):
    """Numeric literal (legacy) - treated as Expression for compatibility"""
    def __init__(self, value):
        self.value = value
    
    def __repr__(self):
        return f"Num({self.value})"


class Str(ASTNode):
    """String literal (legacy) - treated as Expression for compatibility"""
    def __init__(self, value):
        self.value = value
    
    def __repr__(self):
        return f"Str({self.value})"


class Bool(ASTNode):
    """Boolean literal (legacy) - treated as Expression for compatibility"""
    def __init__(self, value):
        self.value = value
    
    def __repr__(self):
        return f"Bool({self.value})"


class If(ASTNode):
    """Conditional statement (legacy)"""
    def __init__(self, condition, then_branch, else_branch=None):
        self.condition = condition
        self.then_branch = then_branch
        self.else_branch = else_branch
    
    def __repr__(self):
        return f"If({self.condition})"


class While(ASTNode):
    """While loop (legacy)"""
    def __init__(self, condition, body):
        self.condition = condition
        self.body = body
    
    def __repr__(self):
        return f"While({self.condition})"


class Print(ASTNode):
    """Print statement (legacy)"""
    def __init__(self, expr):
        self.expr = expr
    
    def __repr__(self):
        return f"Print({self.expr})"


class FunctionDef(ASTNode):
    """Function definition (legacy)"""
    def __init__(self, name, params, body):
        self.name = name
        self.params = params
        self.body = body
    
    def __repr__(self):
        return f"FunctionDef({self.name})"


class FunctionCall(ASTNode):
    """Function call (legacy)"""
    def __init__(self, name, args):
        self.name = name
        self.args = args
    
    def __repr__(self):
        return f"FunctionCall({self.name})"


class TryCatch(ASTNode):
    """Try-catch block (legacy)"""
    def __init__(self, try_block, catch_block):
        self.try_block = try_block
        self.catch_block = catch_block
    
    def __repr__(self):
        return "TryCatch"


class Block(ASTNode):
    """Block of statements (legacy)"""
    def __init__(self, statements):
        self.statements = statements
    
    def __repr__(self):
        return f"Block({len(self.statements)} statements)"


class ListAnchors(ASTNode):
    """List all anchors statement"""
    def __init__(self):
        pass
    
    def __repr__(self):
        return "ListAnchors()"


class DescribeAnchor(ASTNode):
    """Describe specific anchor statement"""
    def __init__(self, anchor_name):
        self.anchor_name = anchor_name
    
    def __repr__(self):
        return f"DescribeAnchor({self.anchor_name})"


# ============================================================================
# MODERN NODES - Enhanced with type safety
# ============================================================================

@dataclass
class Expression(Node):
    """Base class for expressions that evaluate to values"""
    pass


@dataclass
class Statement(Node):
    """Base class for statements that perform actions"""
    pass


# ============================================================================
# LITERAL NODES
# ============================================================================

@dataclass
class NumberLiteral(Expression):
    """Numeric literal (replaces LegacyNum)"""
    value: Union[int, float] = 0
    
    def validate(self):
        if not isinstance(self.value, (int, float)):
            raise TypeError(f"Number literal must be int or float, got {type(self.value)}")
    
    @classmethod
    def from_legacy(cls, node: LegacyNum) -> 'NumberLiteral':
        """Convert legacy Num to modern NumberLiteral"""
        return cls(value=node.value)


@dataclass
class StringLiteral(Expression):
    """String literal (replaces LegacyStr)"""
    value: str = ""
    
    def validate(self):
        if not isinstance(self.value, str):
            raise TypeError(f"String literal must be str, got {type(self.value)}")
    
    @classmethod
    def from_legacy(cls, node: LegacyStr) -> 'StringLiteral':
        """Convert legacy Str to modern StringLiteral"""
        return cls(value=node.value)


@dataclass
class BooleanLiteral(Expression):
    """Boolean literal (replaces LegacyBool)"""
    value: bool = False
    
    def validate(self):
        if not isinstance(self.value, bool):
            raise TypeError(f"Boolean literal must be bool, got {type(self.value)}")
    
    @classmethod
    def from_legacy(cls, node: LegacyBool) -> 'BooleanLiteral':
        """Convert legacy Bool to modern BooleanLiteral"""
        return cls(value=node.value)


# ============================================================================
# PIDGIN SYNTAX NODES (Enhanced)
# ============================================================================

@dataclass
class PidginVariable(Statement):
    """Variable assignment in Pidgin syntax (make, set, wetin be)"""
    identifier: str = ""
    value: Optional[Expression] = None
    assignment_type: str = "set"  # "set", "make", "wetin_be"
    
    def validate(self):
        if self.assignment_type not in ('set', 'make', 'wetin_be'):
            raise ValueError(f"Invalid assignment type: {self.assignment_type}")
        if self.value is not None and not isinstance(self.value, Expression):
            raise TypeError(f"Value must be Expression, got {type(self.value)}")


@dataclass
class PidginPrint(Statement):
    """Print statement in Pidgin syntax (talk, show)"""
    expression: Optional[Expression] = None
    print_type: str = "talk"  # "talk", "show"
    
    def validate(self):
        if self.print_type not in ('talk', 'show'):
            raise ValueError(f"Invalid print type: {self.print_type}")
        if self.expression is not None and not isinstance(self.expression, Expression):
            raise TypeError(f"Expression must be Expression, got {type(self.expression)}")


@dataclass
class PidginBinaryOp(Expression):
    """Binary operation (e.g., a + b, x > y)"""
    left: Optional[Expression] = None
    op: str = "+"
    right: Optional[Expression] = None
    
    def validate(self):
        if self.left is not None and not isinstance(self.left, Expression):
            raise TypeError(f"Left operand must be Expression, got {type(self.left)}")
        if self.right is not None and not isinstance(self.right, Expression):
            raise TypeError(f"Right operand must be Expression, got {type(self.right)}")


@dataclass
class PidginUnaryOp(Expression):
    """Unary operation (e.g., -x, not y)"""
    op: str = "-"
    operand: Optional[Expression] = None
    
    def validate(self):
        if self.operand is not None and not isinstance(self.operand, Expression):
            raise TypeError(f"Operand must be Expression, got {type(self.operand)}")


# ============================================================================
# RELATIONAL SYNTAX NODES
# ============================================================================

class AnchorType(Enum):
    """Type of anchor reference point"""
    STATIC = "static"          # Fixed value (e.g., melting_point = 1510)
    DYNAMIC = "dynamic"        # Computed value (e.g., current_average = lambda: ...)
    CONTEXTUAL = "contextual"  # Context-dependent (e.g., patient_normal varies per patient)
    
    def __repr__(self):
        return f"AnchorType.{self.name}"


@dataclass
class AnchorProperty(Node):
    """
    Property attached to an anchor (e.g., unit="°C", tolerance=5.0)
    
    Example:
        AnchorProperty(key="unit", value=StringLiteral("celsius"))
        AnchorProperty(key="tolerance", value=NumberLiteral(5.0))
    """
    key: str = ""
    value: Optional[Expression] = None
    
    def validate(self):
        if not self.key or not isinstance(self.key, str):
            raise ValueError(f"Property key must be non-empty string, got {self.key}")
        if self.value is not None and not isinstance(self.value, Expression):
            raise TypeError(f"Property value must be Expression, got {type(self.value)}")


@dataclass
class AnchorDeclaration(Statement):
    """
    Declaration of a meaningful reference point (anchor).
    
    Example:
        @anchor optimal_temp = 75.0
            unit = "celsius"
            tolerance = 5.0
            significance = "Peak efficiency at this temperature"
    """
    name: str = ""
    anchor_type: AnchorType = AnchorType.STATIC
    value: Optional[Expression] = None
    properties: List[AnchorProperty] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def validate(self):
        if not self.name or not isinstance(self.name, str):
            raise ValueError(f"Anchor name must be non-empty string, got {self.name}")
        if not isinstance(self.anchor_type, AnchorType):
            raise TypeError(f"Anchor type must be AnchorType, got {type(self.anchor_type)}")
        if self.value is not None and not isinstance(self.value, Expression):
            raise TypeError(f"Anchor value must be Expression, got {type(self.value)}")
        for prop in self.properties:
            if not isinstance(prop, AnchorProperty):
                raise TypeError(f"Property must be AnchorProperty, got {type(prop)}")
    
    def get_property(self, key: str) -> Optional[Expression]:
        """Get property value by key"""
        for prop in self.properties:
            if prop.key == key:
                return prop.value
        return None
    
    def has_property(self, key: str) -> bool:
        """Check if property exists"""
        return self.get_property(key) is not None


@dataclass
class RelativeToClause(Node):
    """
    Specifies which anchors a variable is relative to.
    
    Example:
        relative_to [optimal_temp, danger_threshold, melting_point]
    """
    anchors: List[Union[str, 'AnchorReference']] = field(default_factory=list)
    
    def validate(self):
        if not self.anchors:
            raise ValueError("RelativeToClause must have at least one anchor")
        for anchor in self.anchors:
            if not isinstance(anchor, (str, AnchorReference)):
                raise TypeError(f"Anchor must be str or AnchorReference, got {type(anchor)}")


@dataclass
class AnchorReference(Expression):
    """
    Reference to an anchor, optionally with alias.
    
    Example:
        @optimal_temp as baseline
    """
    name: str = ""
    alias: Optional[str] = None
    
    def validate(self):
        if not self.name or not isinstance(self.name, str):
            raise ValueError(f"Anchor name must be non-empty string, got {self.name}")
        if self.alias is not None and not isinstance(self.alias, str):
            raise TypeError(f"Anchor alias must be string, got {type(self.alias)}")


@dataclass
class RelationalVariable(Statement):
    """
    Declaration of a relational variable that knows its position relative to anchors.
    
    Example:
        relational reactor_temp: f64 = 92.7
            relative_to [optimal_temp, danger_threshold]
            unit = "celsius"
            update_policy = "continuous"
    """
    name: str = ""
    value: Optional[Expression] = None
    relative_to: Optional[RelativeToClause] = None
    properties: Dict[str, Expression] = field(default_factory=dict)
    var_type: Optional[str] = None  # Type annotation (e.g., "f64", "i32")
    
    def validate(self):
        if not self.name or not isinstance(self.name, str):
            raise ValueError(f"Variable name must be non-empty string, got {self.name}")
        # Accept both modern Expression and legacy AST nodes
        if self.value is not None and not isinstance(self.value, (Expression, ASTNode)):
            raise TypeError(f"Variable value must be Expression or ASTNode, got {type(self.value)}")
        if self.relative_to and not isinstance(self.relative_to, RelativeToClause):
            raise TypeError(f"relative_to must be RelativeToClause, got {type(self.relative_to)}")


@dataclass
class RelationalExpression(Expression):
    """
    Expression involving relational operators (is, approaches, enters, etc.)
    
    Examples:
        - temperature is "over" optimal_temp
        - reactor_temp approaches danger_threshold
        - pressure enters safe_range
    """
    left: Optional[Expression] = None
    operator: str = "is"  # "is", "approaches", "enters", "leaves", "crosses"
    right: Optional[Expression] = None
    qualifier: Optional[str] = None  # "over", "under", "near", "within", "far from"
    tolerance: Optional[Expression] = None
    significance: Optional[str] = None  # "CRITICAL", "SIGNIFICANT", "MODERATE", etc.
    
    def validate(self):
        valid_operators = {'is', 'approaches', 'enters', 'leaves', 'crosses', 'trending', ''}
        if self.operator not in valid_operators:
            raise ValueError(f"Operator must be one of {valid_operators}, got {self.operator}")
        # Accept both modern Expression and legacy AST nodes
        if self.left is not None and not isinstance(self.left, (Expression, ASTNode)):
            raise TypeError(f"Left operand must be Expression or ASTNode, got {type(self.left)}")
        if self.right is not None and not isinstance(self.right, (Expression, ASTNode)):
            raise TypeError(f"Right operand must be Expression or ASTNode, got {type(self.right)}")
        if self.tolerance and not isinstance(self.tolerance, (Expression, ASTNode)):
            raise TypeError(f"Tolerance must be Expression or ASTNode, got {type(self.tolerance)}")

@dataclass
class RangeExpression(Expression):
    """
    Represents a range (e.g., 10..20 or optimal_temp ± 5).
    
    Examples:
        - RangeExpression(start=10, end=20)  # 10..20
        - RangeExpression(start=optimal_temp, end=5, is_tolerance=True)  # optimal_temp ± 5
    """
    start: Optional[Expression] = None
    end: Optional[Expression] = None
    is_tolerance: bool = False  # True for ± syntax
    
    def validate(self):
        if self.start is not None and not isinstance(self.start, Expression):
            raise TypeError(f"Range start must be Expression, got {type(self.start)}")
        if self.end is not None and not isinstance(self.end, Expression):
            raise TypeError(f"Range end must be Expression, got {type(self.end)}")


@dataclass
class WhenStatement(Statement):
    """
    Relational control flow statement (like if, but relationship-aware).
    
    Example:
        when reactor_temp is "5 under" danger_threshold:
            action emergency_cooling()
            explanation "Approaching danger zone"
            priority high
    """
    condition: Optional[Union[RelationalExpression, Expression]] = None
    action_block: Optional['ActionBlock'] = None
    priority: Optional[str] = None  # "low", "normal", "high", "critical"
    explanation: Optional[str] = None
    
    def validate(self):
        if self.condition is not None and not isinstance(self.condition, Expression):
            raise TypeError(f"Condition must be Expression, got {type(self.condition)}")
        if self.action_block and not isinstance(self.action_block, ActionBlock):
            raise TypeError(f"Action block must be ActionBlock, got {type(self.action_block)}")
        if self.priority and self.priority not in ('low', 'normal', 'high', 'critical'):
            raise ValueError(f"Invalid priority: {self.priority}")


@dataclass
class ActionBlock(Node):
    """
    Block of actions with metadata.
    
    Example:
        @action increase_cooling(level=5)
        @action send_alert(message="Temperature rising")
        @duration until(temp is "under" warning_threshold)
    """
    actions: List['ActionStatement'] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def validate(self):
        # Validation relaxed - empty action blocks are allowed in Phase 2B
        # Full action block parsing will be implemented in Phase 2C
        for action in self.actions:
            if not isinstance(action, ActionStatement):
                raise TypeError(f"Action must be ActionStatement, got {type(action)}")


@dataclass
class ActionStatement(Statement):
    """
    An action to take in response to a condition.
    
    Example:
        @action emergency_shutdown()
        @explanation "Temperature exceeded safety limits"
        @priority critical
        @duration indefinite
    """
    action: Optional[Expression] = None
    explanation: Optional[str] = None
    priority: Optional[str] = None
    duration: Optional[Expression] = None
    
    def validate(self):
        if self.action is not None and not isinstance(self.action, (Expression, ASTNode)):
            raise TypeError(f"Action must be Expression or ASTNode, got {type(self.action)}")
        if self.priority and self.priority not in ('low', 'normal', 'high', 'critical'):
            raise ValueError(f"Invalid priority: {self.priority}")


@dataclass
class FunctionDeclaration(Statement):
    """
    Function declaration with relational types.
    
    Example:
        @function adjust_temperature(
            @input current: Relation[Anchor],
            @output adjustment: f64
        ) -> f64:
            ...
    """
    name: str = ""
    parameters: List['Parameter'] = field(default_factory=list)
    return_type: Optional['TypeSpecification'] = None
    body: Optional['Block'] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def validate(self):
        if not self.name or not isinstance(self.name, str):
            raise ValueError(f"Function name must be non-empty string, got {self.name}")
        for param in self.parameters:
            if not isinstance(param, Parameter):
                raise TypeError(f"Parameter must be Parameter, got {type(param)}")
        if self.return_type and not isinstance(self.return_type, TypeSpecification):
            raise TypeError(f"Return type must be TypeSpecification, got {type(self.return_type)}")
        if self.body and not isinstance(self.body, Block):
            raise TypeError(f"Body must be Block, got {type(self.body)}")


@dataclass
class Parameter(Node):
    """
    Function parameter with optional decorators.
    
    Example:
        @input current_state: Relation[TemperatureAnchor]
    """
    name: str = ""
    param_type: Optional['TypeSpecification'] = None
    decorators: List[str] = field(default_factory=list)  # "@input", "@output"
    default_value: Optional[Expression] = None
    
    def validate(self):
        if not self.name or not isinstance(self.name, str):
            raise ValueError(f"Parameter name must be non-empty string, got {self.name}")
        if self.param_type and not isinstance(self.param_type, TypeSpecification):
            raise TypeError(f"Parameter type must be TypeSpecification, got {type(self.param_type)}")
        valid_decorators = {'@input', '@output', '@inout'}
        for decorator in self.decorators:
            if decorator not in valid_decorators:
                raise ValueError(f"Invalid decorator: {decorator}, must be one of {valid_decorators}")


@dataclass
class TypeSpecification(Node):
    """
    Type specification for relational types.
    
    Examples:
        - f64
        - Relation[Anchor]
        - Option[i32]
    """
    base_type: str = "Any"  # "Int", "Float", "Relation", "Anchor", etc.
    type_parameters: List['TypeSpecification'] = field(default_factory=list)
    is_optional: bool = False
    
    def validate(self):
        if not self.base_type or not isinstance(self.base_type, str):
            raise ValueError(f"Base type must be non-empty string, got {self.base_type}")
        for param in self.type_parameters:
            if not isinstance(param, TypeSpecification):
                raise TypeError(f"Type parameter must be TypeSpecification, got {type(param)}")
    
    def __str__(self):
        if self.type_parameters:
            params = ', '.join(str(p) for p in self.type_parameters)
            base = f"{self.base_type}[{params}]"
        else:
            base = self.base_type
        return f"Option[{base}]" if self.is_optional else base


# Action blocks omitted - using ActionBlock class above


@dataclass
class OptimizationDirective(Statement):
    """
    Specifies optimization goals for the system.
    
    Example:
        @optimize for:
            - energy_consumption: minimize
            - comfort: maximize
            - cost: minimize
    """
    goals: Dict[str, str] = field(default_factory=dict)  # objective -> "minimize"/"maximize"
    constraints: List[RelationalExpression] = field(default_factory=list)
    
    def validate(self):
        if not self.goals:
            raise ValueError("OptimizationDirective must have at least one goal")
        for objective, direction in self.goals.items():
            if direction not in ('minimize', 'maximize'):
                raise ValueError(f"Goal direction must be 'minimize' or 'maximize', got {direction}")
        for constraint in self.constraints:
            if not isinstance(constraint, RelationalExpression):
                raise TypeError(f"Constraint must be RelationalExpression, got {type(constraint)}")


# ============================================================================
# RELATIONAL OPERATOR NODES (Specialized)
# ============================================================================

@dataclass
class IsExpression(RelationalExpression):
    """
    'is' operator with qualifier (e.g., 'is over', 'is near').
    
    Example:
        temperature is "17.7 over" optimal_temp
    """
    def __post_init__(self):
        self.operator = "is"
        super().__post_init__()


@dataclass
class ApproachesExpression(RelationalExpression):
    """
    'approaches' operator for detecting trends toward a threshold.
    
    Example:
        temperature approaches danger_threshold
    """
    threshold: Optional[Expression] = None  # Custom threshold instead of tolerance
    
    def __post_init__(self):
        self.operator = "approaches"
        super().__post_init__()


@dataclass
class EntersExpression(RelationalExpression):
    """
    'enters' operator for crossing into a range.
    
    Example:
        temperature enters danger_zone
    """
    def __post_init__(self):
        self.operator = "enters"
        super().__post_init__()


@dataclass
class LeavesExpression(RelationalExpression):
    """
    'leaves' operator for crossing out of a range.
    
    Example:
        temperature leaves safe_zone
    """
    def __post_init__(self):
        self.operator = "leaves"
        super().__post_init__()


# ============================================================================
# COMPOUND EXPRESSIONS
# ============================================================================

@dataclass
class LogicalExpression(Expression):
    """
    Logical combination of conditions (and, or, but, except).
    
    Example:
        temperature is "over" optimal AND pressure is "under" max_pressure
    """
    left: Optional[Expression] = None
    operator: str = "and"  # "and", "or", "but", "except"
    right: Optional[Expression] = None
    
    def validate(self):
        valid_operators = {'and', 'or', 'but', 'except', 'xor'}
        if self.operator.lower() not in valid_operators:
            raise ValueError(f"Operator must be one of {valid_operators}, got {self.operator}")
        if self.left is not None and not isinstance(self.left, Expression):
            raise TypeError(f"Left operand must be Expression, got {type(self.left)}")
        if self.right is not None and not isinstance(self.right, Expression):
            raise TypeError(f"Right operand must be Expression, got {type(self.right)}")


@dataclass
class WithProperties(Expression):
    """
    Expression with additional properties.
    
    Example:
        create_relation(value=92.7) with { unit="celsius", confidence=0.95 }
    """
    base: Optional[Expression] = None
    properties: Dict[str, Expression] = field(default_factory=dict)
    
    def validate(self):
        if self.base is not None and not isinstance(self.base, Expression):
            raise TypeError(f"Base must be Expression, got {type(self.base)}")
        for key, value in self.properties.items():
            if not isinstance(key, str):
                raise TypeError(f"Property key must be string, got {type(key)}")
            if not isinstance(value, Expression):
                raise TypeError(f"Property value must be Expression, got {type(value)}")


# ============================================================================
# VISITOR PATTERN SUPPORT
# ============================================================================

class NodeVisitor:
    """
    Base class for AST node visitors.
    
    Usage:
        class MyVisitor(NodeVisitor):
            def visit_AnchorDeclaration(self, node):
                print(f"Found anchor: {node.name}")
                self.generic_visit(node)
        
        visitor = MyVisitor()
        ast.accept(visitor)
    """
    
    def visit(self, node: Node) -> Any:
        """Visit a node"""
        return node.accept(self)
    
    def generic_visit(self, node: Node) -> None:
        """Called if no explicit visitor method exists for a node"""
        for field_name in dir(node):
            if field_name.startswith('_'):
                continue
            field_value = getattr(node, field_name, None)
            if isinstance(field_value, Node):
                self.visit(field_value)
            elif isinstance(field_value, list):
                for item in field_value:
                    if isinstance(item, Node):
                        self.visit(item)
            elif isinstance(field_value, dict):
                for value in field_value.values():
                    if isinstance(value, Node):
                        self.visit(value)


class NodeTransformer(NodeVisitor):
    """
    Base class for AST transformers that modify the tree.
    
    Usage:
        class OptimizeConstants(NodeTransformer):
            def visit_PidginBinaryOp(self, node):
                if isinstance(node.left, NumberLiteral) and isinstance(node.right, NumberLiteral):
                    # Fold constants
                    if node.op == '+':
                        return NumberLiteral(node.left.value + node.right.value)
                return node
    """
    
    def generic_visit(self, node: Node) -> Node:
        """Transform a node and its children"""
        for field_name in dir(node):
            if field_name.startswith('_'):
                continue
            old_value = getattr(node, field_name, None)
            if isinstance(old_value, Node):
                new_value = self.visit(old_value)
                setattr(node, field_name, new_value)
            elif isinstance(old_value, list):
                new_list = []
                for item in old_value:
                    if isinstance(item, Node):
                        new_list.append(self.visit(item))
                    else:
                        new_list.append(item)
                setattr(node, field_name, new_list)
        return node


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def convert_legacy_to_modern(node: LegacyASTNode) -> Optional[Node]:
    """
    Convert legacy AST node to modern node.
    
    Usage:
        legacy_ast = old_parser.parse(tokens)
        modern_ast = convert_legacy_to_modern(legacy_ast)
    """
    if isinstance(node, LegacyVar):
        return Identifier.from_legacy(node)
    elif isinstance(node, LegacyNum):
        return NumberLiteral.from_legacy(node)
    elif isinstance(node, LegacyStr):
        return StringLiteral.from_legacy(node)
    elif isinstance(node, LegacyBool):
        return BooleanLiteral.from_legacy(node)
    elif isinstance(node, LegacyBlock):
        # Recursively convert statements
        modern_statements = []
        for stmt in node.statements:
            modern_stmt = convert_legacy_to_modern(stmt)
            if modern_stmt:
                modern_statements.append(modern_stmt)
        return Block(statements=modern_statements)
    # Add more conversions as needed
    return None


def is_relational_node(node: Node) -> bool:
    """Check if node is a relational programming construct"""
    relational_types = (
        AnchorDeclaration, RelationalVariable, RelationalExpression,
        WhenStatement, ActionBlock, ActionStatement, OptimizationDirective,
        IsExpression, ApproachesExpression, EntersExpression, LeavesExpression
    )
    return isinstance(node, relational_types)


def extract_anchors(ast: Node) -> List[AnchorDeclaration]:
    """Extract all anchor declarations from AST"""
    class AnchorExtractor(NodeVisitor):
        def __init__(self):
            self.anchors = []
        
        def visit_AnchorDeclaration(self, node):
            self.anchors.append(node)
    
    extractor = AnchorExtractor()
    extractor.visit(ast)
    return extractor.anchors


def extract_relational_variables(ast: Node) -> List[RelationalVariable]:
    """Extract all relational variable declarations from AST"""
    class RelationalVarExtractor(NodeVisitor):
        def __init__(self):
            self.variables = []
        
        def visit_RelationalVariable(self, node):
            self.variables.append(node)
    
    extractor = RelationalVarExtractor()
    extractor.visit(ast)
    return extractor.variables


# ============================================================================
# MODULE EXPORTS
# ============================================================================

__all__ = [
    # Base classes
    'Node', 'Expression', 'Statement', 'ASTNode',
    
    # Legacy Pidgin nodes (for backward compatibility)
    'BinOp', 'UnaryOp', 'Assign', 'Var', 'Num', 'Str', 'Bool',
    'If', 'While', 'Print', 'FunctionDef', 'FunctionCall', 'TryCatch', 'Block',
    
    # Literals
    'NumberLiteral', 'StringLiteral', 'BooleanLiteral',
    
    # Pidgin nodes
    'PidginVariable', 'PidginPrint', 'PidginBinaryOp', 'PidginUnaryOp',
    
    # Relational nodes
    'AnchorType', 'AnchorProperty', 'AnchorDeclaration',
    'RelativeToClause', 'AnchorReference', 'RelationalVariable',
    'RelationalExpression', 'RangeExpression',
    'WhenStatement', 'ActionBlock', 'ActionStatement',
    'FunctionDeclaration', 'Parameter', 'TypeSpecification',
    'OptimizationDirective',
    
    # Specialized operators
    'IsExpression', 'ApproachesExpression', 'EntersExpression', 'LeavesExpression',
    
    # Compound expressions
    'LogicalExpression', 'WithProperties',
    
    # Visitors
    'NodeVisitor', 'NodeTransformer',
    
    # Utilities
    'convert_legacy_to_modern', 'is_relational_node',
    'extract_anchors', 'extract_relational_variables',
]
