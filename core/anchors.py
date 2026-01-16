"""
YHWH Language - Anchor Implementation
Genesis 1:1 - In the beginning...

Anchors are first-class reference points that give meaning to values.
They represent significant boundaries, thresholds, or targets in the domain.
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional, List, Dict, Callable
from .types import NumericType
from .exceptions import InvalidAnchorRangeError


@dataclass
class AnchorMetadata:
    """
    Metadata for anchors to track context and significance.
    
    Provides rich contextual information about what an anchor
    represents, where it came from, and how it should be used.
    """
    name: str
    description: str = ""
    unit: Optional[str] = None
    context: str = "default"
    source: str = "program"
    created_at: datetime = field(default_factory=datetime.now)
    confidence: float = 1.0  # 0.0 to 1.0
    
    # Dynamic properties
    is_dynamic: bool = False
    update_function: Optional[Callable] = None
    update_interval: Optional[float] = None  # seconds
    last_updated: Optional[datetime] = None
    
    # Relationships with other anchors
    related_anchors: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        """Validate metadata values."""
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(f"Confidence must be between 0.0 and 1.0, got {self.confidence}")


@dataclass
class Anchor:
    """
    First-class anchor representation.
    
    An anchor is a meaningful reference point in the problem domain.
    Unlike constants, anchors carry semantic meaning and relationships.
    
    Examples:
        - Temperature thresholds (freezing, boiling, optimal)
        - Safety limits (maximum load, critical pressure)
        - Target values (desired heart rate, optimal efficiency)
    
    Attributes:
        name: Unique identifier for this anchor
        value: The reference value (can be dynamic)
        metadata: Rich contextual information
        tolerance: Acceptable deviation from this anchor
        range_start: Optional start of acceptable range
        range_end: Optional end of acceptable range
        buffer_zone: Safety margin around the anchor value
    """
    name: str
    value: Any
    metadata: AnchorMetadata
    
    # Configurable properties
    tolerance: float = 0.0
    range_start: Optional[NumericType] = None
    range_end: Optional[NumericType] = None
    buffer_zone: float = 0.0
    
    # Cached value for dynamic anchors
    _cached_value: Any = field(default=None, init=False, repr=False)
    _cache_timestamp: Optional[datetime] = field(default=None, init=False, repr=False)
    
    def __post_init__(self):
        """Validate anchor properties."""
        if self.range_start is not None and self.range_end is not None:
            if self.range_start > self.range_end:
                raise InvalidAnchorRangeError(self.range_start, self.range_end)
        
        if self.tolerance < 0:
            raise ValueError(f"Tolerance must be non-negative, got {self.tolerance}")
        
        if self.buffer_zone < 0:
            raise ValueError(f"Buffer zone must be non-negative, got {self.buffer_zone}")
        
        # Initialize cached value
        self._cached_value = self.value
        self._cache_timestamp = datetime.now()
    
    @property
    def current_value(self) -> Any:
        """
        Get current anchor value (evaluates dynamic anchors).
        
        For dynamic anchors, checks if cache needs refresh based on
        update_interval. For static anchors, returns stored value.
        
        Returns:
            Current value of the anchor
        """
        if not self.metadata.is_dynamic:
            return self.value
        
        # Check if cache needs refresh
        if self._should_refresh_cache():
            self._refresh_cache()
        
        return self._cached_value
    
    def _should_refresh_cache(self) -> bool:
        """Determine if dynamic anchor cache should be refreshed."""
        if not self.metadata.is_dynamic:
            return False
        
        if self._cache_timestamp is None:
            return True
        
        if self.metadata.update_interval is None:
            return False  # No automatic refresh
        
        elapsed = (datetime.now() - self._cache_timestamp).total_seconds()
        return elapsed >= self.metadata.update_interval
    
    def _refresh_cache(self):
        """Refresh cached value for dynamic anchor."""
        if self.metadata.update_function is not None:
            try:
                self._cached_value = self.metadata.update_function()
                self._cache_timestamp = datetime.now()
                self.metadata.last_updated = datetime.now()
            except Exception as e:
                # Keep old cached value on error
                print(f"Warning: Failed to update dynamic anchor '{self.name}': {e}")
    
    def evaluate(self, context: Optional[Dict] = None) -> Any:
        """
        Evaluate anchor value with optional context.
        
        Args:
            context: Optional execution context for dynamic evaluation
            
        Returns:
            Evaluated anchor value
        """
        if self.metadata.is_dynamic and self.metadata.update_function:
            if context is not None:
                # Pass context to update function if it accepts it
                try:
                    return self.metadata.update_function(context)
                except TypeError:
                    # Function doesn't accept context
                    return self.metadata.update_function()
            return self.current_value
        
        return self.value
    
    def distance_to(self, other: Any) -> float:
        """
        Calculate distance to another anchor or value.
        
        Args:
            other: Another Anchor instance or numeric value
            
        Returns:
            Absolute distance between this anchor and the other value
            
        Note:
            For non-numeric types, returns 0.0 (custom metrics needed)
        """
        current = self.current_value
        
        if isinstance(other, Anchor):
            other_value = other.current_value
        else:
            other_value = other
        
        if isinstance(current, (int, float)) and isinstance(other_value, (int, float)):
            return abs(float(current) - float(other_value))
        
        # For non-numeric types, subclasses should override this
        return 0.0
    
    def is_within_range(self, value: NumericType, use_buffer: bool = True) -> bool:
        """
        Check if value falls within anchor's acceptable range.
        
        Args:
            value: Value to check
            use_buffer: Whether to include buffer zone in range
            
        Returns:
            True if value is within range, False otherwise
        """
        if self.range_start is None or self.range_end is None:
            return True  # No range constraint
        
        buffer = self.buffer_zone if use_buffer else 0.0
        return (self.range_start - buffer) <= value <= (self.range_end + buffer)
    
    def is_critical_threshold(self) -> bool:
        """
        Determine if this anchor represents a critical threshold.
        
        Critical anchors have small or zero tolerance, indicating
        strict boundaries that should not be crossed.
        
        Returns:
            True if this is a critical threshold
        """
        return self.tolerance < 0.01 or self.buffer_zone == 0.0
    
    def __repr__(self) -> str:
        """String representation for debugging."""
        dynamic = " (dynamic)" if self.metadata.is_dynamic else ""
        return f"Anchor({self.name}={self.current_value}{dynamic})"
    
    def __str__(self) -> str:
        """Human-readable string representation."""
        return f"{self.name}: {self.current_value}"


class AnchorRegistry:
    """
    Registry for managing anchors in a context.
    
    Provides centralized management of anchors with support for
    dependencies, updates, and queries.
    """
    
    def __init__(self):
        self._anchors: Dict[str, Anchor] = {}
        self._dependency_graph: Dict[str, List[str]] = {}
    
    def register(self, anchor: Anchor):
        """Register an anchor in the registry."""
        self._anchors[anchor.name] = anchor
        
        # Build dependency graph
        if anchor.metadata.dependencies:
            self._dependency_graph[anchor.name] = anchor.metadata.dependencies
    
    def get(self, name: str) -> Optional[Anchor]:
        """Get anchor by name."""
        return self._anchors.get(name)
    
    def get_all(self) -> Dict[str, Anchor]:
        """Get all registered anchors."""
        return self._anchors.copy()
    
    def find_by_context(self, context: str) -> List[Anchor]:
        """Find all anchors in a specific context."""
        return [
            anchor for anchor in self._anchors.values()
            if anchor.metadata.context == context
        ]
    
    def find_by_type(self, value_type: type) -> List[Anchor]:
        """Find all anchors matching a specific value type."""
        return [
            anchor for anchor in self._anchors.values()
            if isinstance(anchor.current_value, value_type)
        ]
    
    def update_dynamic_anchors(self):
        """Update all dynamic anchors that need refresh."""
        for anchor in self._anchors.values():
            if anchor.metadata.is_dynamic and anchor._should_refresh_cache():
                anchor._refresh_cache()
    
    def get_dependents(self, anchor_name: str) -> List[str]:
        """Get all anchors that depend on the given anchor."""
        dependents = []
        for name, deps in self._dependency_graph.items():
            if anchor_name in deps:
                dependents.append(name)
        return dependents
