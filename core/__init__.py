"""
YHWH Language Core - Relational Programming Paradigm
Genesis 1:1 - In the beginning...

This module implements the core relational programming paradigm where
values are not just numbers, but relationships with meaning.

Core Concepts:
--------------
- Anchors: Meaningful reference points (thresholds, targets, limits)
- Relations: Values that know their position relative to anchors
- Context: Runtime environment managing anchors and relations
- Optimizer: Multi-objective decision making

Example Usage:
--------------
    from core import Anchor, Relation, RelationalContext, AnchorMetadata
    
    # Define meaningful reference points
    optimal_temp = Anchor(
        name="optimal",
        value=75.0,
        metadata=AnchorMetadata(
            name="optimal",
            description="Optimal operating temperature",
            unit="°C"
        ),
        tolerance=2.0
    )
    
    danger_temp = Anchor(
        name="danger",
        value=100.0,
        metadata=AnchorMetadata(
            name="danger",
            description="Danger threshold",
            unit="°C"
        ),
        tolerance=1.0
    )
    
    # Create relational context
    ctx = RelationalContext()
    ctx.add_anchor(optimal_temp)
    ctx.add_anchor(danger_temp)
    
    # Create relational variable
    temperature = ctx.create_relation(
        "reactor_temp",
        92.7,
        anchor_names=["optimal", "danger"]
    )
    
    # The system now "understands" what 92.7 means:
    print(temperature.relation_to("optimal"))  # "17.7 over optimal"
    print(temperature.relation_to("danger"))   # "7.3 under danger"
    print(temperature.significance_to("danger"))  # CRITICAL
    
    # Get suggested actions
    actions = temperature.suggested_actions()
    for action in actions:
        print(f"{action['type']} by {action['amount']}: {action['reason']}")

Public API:
-----------
Types:
    - RelationSignificance: NEGLIGIBLE, NOTICEABLE, SIGNIFICANT, CRITICAL, EXTREME
    - PriorityLevel: LOW, NORMAL, HIGH, CRITICAL
    - RelationQualifier: EQUAL_TO, OVER, UNDER, NEAR, FAR_FROM, etc.
    - OptimizationGoal: MINIMIZE, MAXIMIZE

Core Classes:
    - Anchor: First-class reference point
    - AnchorMetadata: Contextual information about anchors
    - AnchorRegistry: Centralized anchor management
    - Relation: Value with relational awareness
    - RelationalContext: Runtime environment
    - OptimizationEngine: Multi-objective optimization

Exceptions:
    - RelationalError: Base exception
    - AnchorError: Anchor-related errors
    - AnchorNotFoundError: Missing anchor
    - InvalidAnchorRangeError: Invalid range definition
    - RelationError: Relation-related errors
    - IncompatibleTypesError: Type mismatch
    - ContextError: Context operation errors
    - OptimizationError: Optimization failures
"""

# Version info
__version__ = "0.1.0"
__author__ = "GIANT Language Team"

# Core types
from .types import (
    RelationSignificance,
    PriorityLevel,
    RelationQualifier,
    OptimizationGoal,
    NumericType,
    T
)

# Exceptions
from .exceptions import (
    RelationalError,
    AnchorError,
    AnchorNotFoundError,
    InvalidAnchorRangeError,
    RelationError,
    IncompatibleTypesError,
    ContextError,
    OptimizationError
)

# Anchor system
from .anchors import (
    Anchor,
    AnchorMetadata,
    AnchorRegistry
)

# Relation system
from .relations import Relation

# Context management
from .context import RelationalContext

# Optimization
from .optimizer import (
    OptimizationEngine,
    Objective,
    Constraint
)

# Public API
__all__ = [
    # Types
    "RelationSignificance",
    "PriorityLevel",
    "RelationQualifier",
    "OptimizationGoal",
    "NumericType",
    "T",
    
    # Exceptions
    "RelationalError",
    "AnchorError",
    "AnchorNotFoundError",
    "InvalidAnchorRangeError",
    "RelationError",
    "IncompatibleTypesError",
    "ContextError",
    "OptimizationError",
    
    # Anchor system
    "Anchor",
    "AnchorMetadata",
    "AnchorRegistry",
    
    # Relation system
    "Relation",
    
    # Context
    "RelationalContext",
    
    # Optimization
    "OptimizationEngine",
    "Objective",
    "Constraint",
]
