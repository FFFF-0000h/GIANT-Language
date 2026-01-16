"""
YHWH Language - Core Type Definitions
Genesis 1:1 - In the beginning...

Enums and type definitions for relational programming.
"""
from enum import Enum
from typing import TypeVar, Union


# Type variables for generic programming
T = TypeVar('T')
NumericType = Union[int, float]


class RelationSignificance(Enum):
    """
    Significance levels for relational changes.
    
    Maps distance from anchor to meaningful categories:
    - NEGLIGIBLE: Within noise threshold
    - NOTICEABLE: Measurable but not concerning
    - SIGNIFICANT: Requires attention
    - CRITICAL: Urgent action needed
    - EXTREME: Crisis level
    """
    NEGLIGIBLE = "negligible"
    NOTICEABLE = "noticeable"
    SIGNIFICANT = "significant"
    CRITICAL = "critical"
    EXTREME = "extreme"
    
    def __lt__(self, other):
        """Allow comparison of significance levels."""
        if not isinstance(other, RelationSignificance):
            return NotImplemented
        
        order = [
            RelationSignificance.NEGLIGIBLE,
            RelationSignificance.NOTICEABLE,
            RelationSignificance.SIGNIFICANT,
            RelationSignificance.CRITICAL,
            RelationSignificance.EXTREME
        ]
        return order.index(self) < order.index(other)
    
    def __le__(self, other):
        return self == other or self < other
    
    def __gt__(self, other):
        return not self <= other
    
    def __ge__(self, other):
        return not self < other


class PriorityLevel(Enum):
    """
    Priority levels for actions and decisions.
    
    Used to rank competing actions when multiple
    relational conditions trigger simultaneously.
    """
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"
    
    @property
    def numeric_value(self) -> int:
        """Get numeric representation for sorting."""
        return {
            PriorityLevel.LOW: 1,
            PriorityLevel.NORMAL: 2,
            PriorityLevel.HIGH: 3,
            PriorityLevel.CRITICAL: 4
        }[self]
    
    def __lt__(self, other):
        if not isinstance(other, PriorityLevel):
            return NotImplemented
        return self.numeric_value < other.numeric_value
    
    def __le__(self, other):
        return self == other or self < other
    
    def __gt__(self, other):
        return not self <= other
    
    def __ge__(self, other):
        return not self < other


class RelationQualifier(Enum):
    """
    Qualifiers for relational comparisons.
    
    These express the relationship between a value
    and its anchor in meaningful terms.
    """
    EQUAL_TO = "equal_to"
    OVER = "over"
    UNDER = "under"
    NEAR = "near"
    FAR_FROM = "far_from"
    WITHIN = "within"
    APPROACHING = "approaching"
    RECEDING_FROM = "receding_from"
    APPROXIMATELY = "approximately"


class OptimizationGoal(Enum):
    """Optimization goal types."""
    MINIMIZE = "minimize"
    MAXIMIZE = "maximize"
