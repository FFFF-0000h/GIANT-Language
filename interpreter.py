"""Interpreter: Executes the AST with relational programming support.

Implements the YorubaNumeralSystem paradigm where numbers have meaning and relationships
are first-class.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
from relational.ast_nodes import (
    AnchorDeclaration, RelationalVariable, WhenStatement, OptimizationDirective,
    ActionStatement, ActionBlock, RelationalExpression, IsExpression,
    Assign, Var, Num, Str, Bool, BinOp, UnaryOp, If, While, Print, Block,
    FunctionDef, FunctionCall, TryCatch, ListAnchors, DescribeAnchor,
    NumberLiteral, StringLiteral, BooleanLiteral
)
from math_operations import MathOperations

# Import core runtime for relational semantics
try:
    from core import (
        Anchor, Relation, RelationalContext, OptimizationEngine,
        AnchorMetadata, RelationSignificance, PriorityLevel
    )
    CORE_AVAILABLE = True
except ImportError:
    CORE_AVAILABLE = False
    print("Warning: Core runtime not available. Relational features disabled.")


class Interpreter:
    """
    Unified interpreter for GIANT Language supporting both Pidgin and Relational paradigms.
    
    Architecture:
        - Pidgin: Traditional variable assignments, control flow
        - Relational: Anchors, relations, when-clauses, optimization
        - Hybrid: Seamlessly mix both styles
    
    Key Concepts (YorubaNumeralSystem):
        - Anchors: Meaningful reference points (not just constants)
        - Relations: Values that know their position relative to anchors
        - When-clauses: Context-aware conditions
        - Explanations: Built-in rationale for decisions
    """
    
    def __init__(self, enable_explanations: bool = True) -> None:
        """Initialize interpreter with optional explanation mode.
        
        Args:
            enable_explanations: Whether to print explanations of operations
        """
        # Pidgin interpreter state
        self.variables: Dict[str, Any] = {}
        self.functions: Dict[str, Any] = {}
        self.math_ops = MathOperations()
        
        # Relational interpreter state
        if CORE_AVAILABLE:
            self.relational_context = RelationalContext()
            self.optimization_engine = OptimizationEngine()
        else:
            self.relational_context = None
            self.optimization_engine = None
        
        # Configuration
        self.enable_explanations = enable_explanations
        self.execution_log: List[Dict[str, Any]] = []

    def interpret(self, node) -> Any:
        """
        Main interpretation entry point.
        Handles both legacy Pidgin nodes and modern Relational nodes.
        """
        # Block of statements
        if isinstance(node, Block):
            result = None
            for stmt in node.statements:
                result = self.interpret(stmt)
            return result
        
        # ====================================================================
        # ANCHOR MANAGEMENT NODES
        # ====================================================================
        
        elif isinstance(node, ListAnchors):
            return self.interpret_list_anchors(node)
        
        elif isinstance(node, DescribeAnchor):
            return self.interpret_describe_anchor(node)
        
        # ====================================================================
        # RELATIONAL NODES (YorubaNumeralSystem Implementation)
        # ====================================================================
        
        elif isinstance(node, AnchorDeclaration):
            return self.interpret_anchor_declaration(node)
        
        elif isinstance(node, RelationalVariable):
            return self.interpret_relational_variable(node)
        
        elif isinstance(node, WhenStatement):
            return self.interpret_when_statement(node)
        
        elif isinstance(node, OptimizationDirective):
            return self.interpret_optimization_directive(node)
        
        # ====================================================================
        # PIDGIN NODES (Legacy Compatibility)
        # ====================================================================
        
        elif isinstance(node, Assign):
            result, error = self.evaluate(node.expr)
            if error:
                print(f"Error: {error}")
            else:
                self.variables[node.var] = result
                return result
        
        elif isinstance(node, If):
            result, error = self.evaluate(node.condition)
            if error:
                print(f"Error: {error}")
            elif result:
                self.interpret(node.then_branch)
            elif node.else_branch:
                self.interpret(node.else_branch)
        
        elif isinstance(node, While):
            while True:
                result, error = self.evaluate(node.condition)
                if error:
                    print(f"Error: {error}")
                    break
                if not result:
                    break
                self.interpret(node.body)
        
        elif isinstance(node, Print):
            result, error = self.evaluate(node.expr)
            if error:
                print(f"{error}")
            else:
                print(result)
                return result
        
        elif isinstance(node, FunctionDef):
            self.functions[node.name] = node
            return node
        
        elif isinstance(node, FunctionCall):
            func = self.functions.get(node.name)
            if func:
                # Simple call without args for now
                self.interpret(func.body)
        
        elif isinstance(node, TryCatch):
            try:
                self.interpret(node.try_block)
            except:
                self.interpret(node.catch_block)
        
        # Default: try to evaluate as expression
        else:
            result, error = self.evaluate(node)
            if error and self.enable_explanations:
                print(f"{error}")
            return result
    
    # ========================================================================
    # ANCHOR MANAGEMENT INTERPRETATION
    # ========================================================================
    
    def interpret_list_anchors(self, node: ListAnchors) -> None:
        """
        List all declared anchors with their basic information.
        """
        if not CORE_AVAILABLE or not self.relational_context:
            print("Warning: No relational context available")
            return None
        
        anchors = self.relational_context.anchor_registry.get_all()
        
        if not anchors:
            print("No anchors defined.")
            return None
        
        print(f"\nRegistered Anchors ({len(anchors)}):")
        print("-" * 50)
        for anchor_name, anchor in anchors.items():
            print(f"  {anchor.name}: {anchor.value} (tolerance: ±{anchor.tolerance})")
        
        return None
    
    def interpret_describe_anchor(self, node: DescribeAnchor) -> None:
        """
        Display full details of a specific anchor.
        """
        if not CORE_AVAILABLE or not self.relational_context:
            print("Warning: No relational context available")
            return None
        
        anchor_name = node.anchor_name
        
        # Check if anchor exists
        if not self.relational_context.has_anchor(anchor_name):
            print(f"Error: Anchor '{anchor_name}' not found")
            return None
        
        anchor = self.relational_context.get_anchor(anchor_name)
        
        # Display all anchor properties
        print(f"Anchor: {anchor.name}")
        print(f"  Value: {anchor.value}")
        print(f"  Tolerance: ±{anchor.tolerance}")
        
        if anchor.metadata.unit:
            print(f"  Unit: {anchor.metadata.unit}")
        
        if anchor.metadata.description:
            print(f"  Description: {anchor.metadata.description}")
        
        print(f"  Context: {anchor.metadata.context}")
        print(f"  Confidence: {anchor.metadata.confidence}")
        
        if anchor.range_start is not None and anchor.range_end is not None:
            print(f"  Range: [{anchor.range_start}, {anchor.range_end}]")
        
        if anchor.metadata.created_at:
            print(f"  Created: {anchor.metadata.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
        
        return None
    
    # ========================================================================
    # RELATIONAL INTERPRETATION (YorubaNumeralSystem Implementation)
    # ========================================================================
    
    def interpret_anchor_declaration(self, node: AnchorDeclaration) -> Optional['Anchor']:
        """
        Create and register an anchor - a meaningful reference point.
        
        YorubaNumeralSystem Concept:
            Anchors aren't just constants - they have domain knowledge:
            - Tolerance zones
            - Significance levels
            - Context metadata
        
        Example:
            @anchor optimal_temp = 75.0
                unit = "celsius"
                tolerance = 5.0
        """
        if not CORE_AVAILABLE:
            if self.enable_explanations:
                print(f"Warning: Anchor '{node.name}' declared but core runtime unavailable")
            return None
        
        # Evaluate anchor value
        value, error = self.evaluate(node.value)
        if error:
            print(f"Error: Anchor error: {error}")
            return None
        
        # Build metadata from properties
        metadata = {'description': '', 'context': 'default'}
        tolerance = 0.0
        range_start = None
        range_end = None
        
        for prop in node.properties:
            prop_value, prop_error = self.evaluate(prop.value)
            if not prop_error:
                metadata[prop.key] = prop_value
                
                # Extract special properties
                if prop.key == 'tolerance':
                    tolerance = float(prop_value)
                elif prop.key == 'range_start':
                    range_start = float(prop_value)
                elif prop.key == 'range_end':
                    range_end = float(prop_value)
        
        # Create anchor metadata
        anchor_metadata = AnchorMetadata(
            name=node.name,
            description=metadata.get('description', ''),
            unit=metadata.get('unit', ''),
            context=metadata.get('context', 'default'),
            confidence=metadata.get('confidence', 1.0)
        )
        
        # Create anchor
        anchor = Anchor(
            name=node.name,
            value=value,
            metadata=anchor_metadata,
            tolerance=tolerance,
            range_start=range_start,
            range_end=range_end
        )
        
        # Register in context
        self.relational_context.add_anchor(anchor)
        
        if self.enable_explanations:
            print(f"Anchor '{node.name}' = {value} (tolerance: ±{tolerance})")
        
        return anchor
    
    def interpret_relational_variable(self, node: RelationalVariable) -> Optional['Relation']:
        """
        Create a relational variable that knows its position relative to anchors.
        
        YorubaNumeralSystem Concept:
            Variables aren't just buckets for values - they understand their
            meaning in context:
            - "17.7 over optimal_efficiency"
            - "7.3 under melting_point"
            - SIGNIFICANCE is automatic
        
        Example:
            relational reactor_temp = 92.7 relative_to [optimal_temp, danger_threshold]
        """
        if not CORE_AVAILABLE:
            # Fallback: treat as regular variable
            value, error = self.evaluate(node.value)
            if not error:
                self.variables[node.name] = value
            return None
        
        # Evaluate value
        value, error = self.evaluate(node.value)
        if error:
            print(f"Error: Variable error: {error}")
            return None
        
        # Determine anchor references
        anchor_names = []
        if node.relative_to:
            anchor_names = node.relative_to.anchors
        else:
            # Auto-detect relevant anchors
            anchor_names = list(self.relational_context.anchor_registry.anchors.keys())
        
        # Create relation
        relation = self.relational_context.create_relation(
            name=node.name,
            value=value,
            anchor_names=anchor_names
        )
        
        # Apply properties
        for key, expr in (node.properties or {}).items():
            prop_value, _ = self.evaluate(expr)
            relation.metadata[key] = prop_value
        
        # Store in variables for hybrid access
        self.variables[node.name] = relation
        
        if self.enable_explanations:
            relations = []
            for anchor_name in anchor_names:
                if self.relational_context.has_anchor(anchor_name):
                    rel_text = relation.relation_to(anchor_name)
                    significance = relation.significance_to(anchor_name)
                    relations.append(f"{rel_text} ({significance.value})")
            
            # Build property display
            prop_display = ""
            if node.properties:
                prop_parts = []
                for key, expr in node.properties.items():
                    prop_value, _ = self.evaluate(expr)
                    if isinstance(prop_value, str):
                        prop_parts.append(f"{key}=\"{prop_value}\"")
                    else:
                        prop_parts.append(f"{key}={prop_value}")
                if prop_parts:
                    prop_display = " [" + ", ".join(prop_parts) + "]"
            
            if relations:
                relations_str = ", ".join(relations[:2])  # Show first 2
                print(f"Relational '{node.name}' = {value} | {relations_str}{prop_display}")
            else:
                print(f"Relational '{node.name}' = {value}{prop_display}")
        
        return relation
    
    def interpret_when_statement(self, node: WhenStatement) -> bool:
        """
        Execute when-clause with relational condition.
        
        YorubaNumeralSystem Concept:
            Control flow responds to RELATIONSHIPS, not just raw values:
            - "approaching danger threshold"
            - "enters optimal range"
            - Context-aware, self-explanatory
        
        Example:
            when reactor_temp is "5 under" danger_threshold:
                action increase_cooling()
        """
        # Evaluate condition
        condition_result, error = self.evaluate(node.condition)
        
        if error:
            if self.enable_explanations:
                print(f"Error: When condition error: {error}")
            return False
        
        if condition_result:
            # Condition triggered
            if self.enable_explanations:
                explanation = getattr(node.action_block, 'explanation', '')
                if explanation:
                    print(f"Triggered: {explanation}")
                else:
                    print(f"When condition met, executing actions")
            
            # Execute action block
            for action_stmt in node.action_block.actions:
                # ActionStatement has 'action' field which can be any node
                if hasattr(action_stmt, 'action') and action_stmt.action:
                    self.interpret(action_stmt.action)
                elif hasattr(action_stmt, 'statement'):  # Legacy support
                    self.interpret(action_stmt.statement)
            
            # Log execution
            self._log_execution(node, True)
            return True
        
        return False
    
    def interpret_optimization_directive(self, node: OptimizationDirective) -> None:
        """
        Configure optimization goals.
        
        YorubaNumeralSystem Concept:
            Systems can optimize for MULTIPLE competing goals:
            - Minimize energy AND maximize comfort
            - Explicit tradeoffs
        
        Example:
            @optimize for:
                - energy: minimize
                - comfort: maximize
        """
        if not CORE_AVAILABLE or not self.optimization_engine:
            if self.enable_explanations:
                print("Warning: Optimization engine unavailable")
            return
        
        # Add objectives
        for goal_name, direction in (node.goals or {}).items():
            self.optimization_engine.add_objective(goal_name, direction)
        
        if self.enable_explanations:
            goals = [f"{name}:{type}" for name, type in (node.goals or {}).items()]
            print(f"Optimize for: {', '.join(goals)}")
    
    # ========================================================================
    # EXPRESSION EVALUATION (Pidgin + Relational)
    # ========================================================================
    
    def evaluate(self, node) -> Tuple[Any, Optional[str]]:
        """
        Evaluate an expression node.
        Supports both Pidgin expressions and Relational expressions.
        
        Returns:
            (result, error_message): Tuple of (value, None) on success,
                                     or (None, error_message) on failure.
        """
        # ====================================================================
        # LITERALS
        # ====================================================================
        
        if isinstance(node, Num):
            return (node.value, None)
        
        elif isinstance(node, Str):
            return (node.value, None)
        
        elif isinstance(node, Bool):
            return (node.value, None)
        
        elif isinstance(node, NumberLiteral):
            return (node.value, None)
        
        elif isinstance(node, StringLiteral):
            return (node.value, None)
        
        elif isinstance(node, BooleanLiteral):
            return (node.value, None)
        
        # ====================================================================
        # VARIABLES
        # ====================================================================
        
        elif isinstance(node, Var):
            value = self.variables.get(node.name)
            if value is None:
                # Check relational context for relational variables
                if CORE_AVAILABLE and self.relational_context:
                    rel_var = self.relational_context.variables.get(node.name)
                    if rel_var:
                        return (rel_var.value, None)
                    
                    # Check for anchors in the anchor registry
                    anchor = self.relational_context.anchor_registry.get(node.name)
                    if anchor:
                        return (anchor.value, None)
                
                return (None, f"Wahala! Variable '{node.name}' no set yet!")
            return (value, None)
        
        # ====================================================================
        # RELATIONAL EXPRESSIONS
        # ====================================================================
        
        elif isinstance(node, IsExpression) or isinstance(node, RelationalExpression):
            return self.evaluate_relational_expression(node)
        
        # ====================================================================
        # BINARY OPERATIONS
        # ====================================================================
        
        elif isinstance(node, BinOp):
            left_val, left_error = self.evaluate(node.left)
            if left_error:
                return (None, left_error)
            
            right_val, right_error = self.evaluate(node.right)
            if right_error:
                return (None, right_error)
            
            return MathOperations.evaluate_operation(left_val, node.op, right_val)
        
        # ====================================================================
        # UNARY OPERATIONS
        # ====================================================================
        
        elif isinstance(node, UnaryOp):
            operand_val, operand_error = self.evaluate(node.operand)
            if operand_error:
                return (None, operand_error)
            
            return MathOperations.evaluate_unary_operation(operand_val, node.op)
        
        # ====================================================================
        # DEFAULT
        # ====================================================================
        
        return (None, "Wahala! I no understand dat expression!")
    
    def evaluate_relational_expression(self, node: RelationalExpression) -> Tuple[bool, Optional[str]]:
        """
        Evaluate relational expression using YorubaNumeralSystem semantics.
        
        YorubaNumeralSystem Concept:
            - "is over" → positional relationship
            - "is near" → within tolerance
            - "approaches" → trending toward
            - "enters" → crossing into range
        
        Examples:
            temperature is "over" optimal_temp
            pressure approaches danger_threshold
            speed enters safe_range
        """
        # Evaluate left operand
        left_val, left_error = self.evaluate(node.left)
        if left_error:
            return (False, left_error)
        
        # If left side is a Relation object, extract the value
        if CORE_AVAILABLE and isinstance(left_val, Relation):
            left_val = left_val.value
        
        # Evaluate right operand (often an anchor reference)
        right_val, right_error = self.evaluate(node.right)
        if right_error:
            return (False, right_error)
        
        # Check if right side is an anchor
        anchor = None
        anchor_name = None
        if isinstance(node.right, Var):
            anchor_name = node.right.name
            if CORE_AVAILABLE and self.relational_context:
                anchor = self.relational_context.anchor_registry.get(anchor_name)
                if anchor:
                    right_val = anchor.value
        
        # Handle different operators
        operator = getattr(node, 'operator', 'is')
        qualifier = getattr(node, 'qualifier', None)
        
        try:
            if operator == 'is':
                result = self._evaluate_is_operator(
                    left_val, right_val, qualifier, anchor
                )
                return (result, None)
            
            elif operator == 'approaches':
                result = self._evaluate_approaches_operator(
                    left_val, right_val, anchor, node
                )
                return (result, None)
            
            elif operator == 'enters':
                result = self._evaluate_enters_operator(
                    left_val, right_val, node
                )
                return (result, None)
            
            elif operator == 'leaves':
                result = left_val < right_val  # Simplified
                return (result, None)
            
            elif operator == 'crosses':
                # Would need historical tracking
                result = abs(left_val - right_val) < 0.1
                return (result, None)
            
            elif operator == '':
                # Empty operator, just return the value
                return (left_val, None)
            
            else:
                return (False, f"Unknown relational operator: {operator}")
        
        except Exception as e:
            return (False, f"Relational evaluation error: {str(e)}")
    
    def _evaluate_is_operator(self, left_val: float, right_val: float, 
                             qualifier: Optional[str], anchor: Optional['Anchor']) -> bool:
        """
        Evaluate 'is' operator with qualifier.
        
        Qualifiers:
            - "over" → greater than
            - "under" → less than
            - "near" → within tolerance
            - "equal_to" → exactly equal
            - "approximately" → within 5%
        """
        if qualifier == 'over':
            return left_val > right_val
        
        elif qualifier == 'under':
            return left_val < right_val
        
        elif qualifier == 'near':
            # Use anchor tolerance if available
            if anchor:
                distance = abs(left_val - right_val)
                return distance <= anchor.tolerance
            else:
                # Default: within 10%
                return abs(left_val - right_val) <= (right_val * 0.1)
        
        elif qualifier == 'equal_to' or qualifier == '':
            return left_val == right_val
        
        elif qualifier == 'approximately':
            # Within 5% by default
            return abs(left_val - right_val) <= (right_val * 0.05)
        
        else:
            # Default to equality
            return left_val == right_val
    
    def _evaluate_approaches_operator(self, left_val: float, right_val: float,
                                     anchor: Optional['Anchor'], node) -> bool:
        """
        Evaluate 'approaches' operator.
        
        YorubaNumeralSystem Concept:
            "Approaching" means:
            - Within threshold distance (10% or tolerance)
            - Trending toward (if we track history)
        """
        tolerance = getattr(node, 'tolerance', None)
        
        if tolerance is None:
            # Use anchor tolerance or default to 10%
            if anchor:
                tolerance = anchor.tolerance
            else:
                tolerance = right_val * 0.1
        
        distance = abs(left_val - right_val)
        return distance <= tolerance
    
    def _evaluate_enters_operator(self, left_val: float, right_val: float, node) -> bool:
        """
        Evaluate 'enters' operator for range checking.
        
        Note: True "enters" would require tracking previous values
        to detect crossing. For now, we do simple range check.
        """
        if isinstance(node.right, RangeExpression):
            # Range expression
            range_start, _ = self.evaluate(node.right.start)
            range_end, _ = self.evaluate(node.right.end)
            return range_start <= left_val <= range_end
        else:
            # Simple value - check if near
            return abs(left_val - right_val) < 1.0
    
    # ========================================================================
    # UTILITY METHODS
    # ========================================================================
    
    def _log_execution(self, node, result):
        """Log execution for debugging and explanation"""
        if self.enable_explanations:
            log_entry = {
                'node': type(node).__name__,
                'result': str(result),
                'timestamp': datetime.now().isoformat()
            }
            self.execution_log.append(log_entry)
    
    def get_variable_explanation(self, var_name: str) -> str:
        """
        Get human-readable explanation of a variable's value.
        
        YorubaNumeralSystem Concept:
            Variables can explain themselves in context
        """
        if var_name not in self.variables:
            return f"Variable '{var_name}' not defined"
        
        value = self.variables[var_name]
        
        # Check if it's a relational variable
        if CORE_AVAILABLE and isinstance(value, Relation):
            explanations = []
            for anchor_name in value.anchors.keys():
                rel_text = value.relation_to(anchor_name)
                sig = value.significance_to(anchor_name)
                explanations.append(f"{rel_text} ({sig.value})")
            
            return f"{var_name} = {value.current_value}: " + ", ".join(explanations)
        else:
            return f"{var_name} = {value}"
    
    # ========================================================================
    # LEGACY COMPATIBILITY
    # ========================================================================
    
    def evaluate_expression(self, operand1, operator, operand2):
        """
        Legacy method for backward compatibility with existing tests.
        """
        return MathOperations.evaluate_operation(operand1, operator, operand2)
