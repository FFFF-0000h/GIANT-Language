"""
GIANT Language - Relation Implementation
Genesis 1:1 - In the beginning...

Relations are values that know their position relative to anchors.
They carry semantic meaning about what values represent in context.
"""
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from .anchors import Anchor
from .types import RelationSignificance, PriorityLevel, RelationQualifier, NumericType
from .exceptions import AnchorNotFoundError, IncompatibleTypesError


@dataclass
class Relation:
    """
    Core relational value that knows its anchors.
    
    A Relation is not just a value - it's a value with awareness
    of its meaning through relationships to anchors.
    
    Example:
        temperature = Relation(
            value=92.7,
            anchors={
                "optimal": Anchor("optimal", 75),
                "danger": Anchor("danger", 100)
            }
        )
        # This temperature "knows" it's:
        # - 17.7 over optimal
        # - 7.3 under danger
        # - in the "concerning but not critical" zone
    
    Attributes:
        value: The actual value
        anchors: Dictionary mapping anchor names to Anchor objects
        metadata: Additional contextual information
    """
    value: Any
    anchors: Dict[str, Anchor]
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Cached computations for performance
    _distances: Dict[str, float] = field(default_factory=dict, init=False, repr=False)
    _significance_cache: Dict[str, RelationSignificance] = field(
        default_factory=dict, init=False, repr=False
    )
    _qualifier_cache: Dict[str, RelationQualifier] = field(
        default_factory=dict, init=False, repr=False
    )
    
    def __post_init__(self):
        """Initialize relational computations."""
        self._compute_distances()
        self._invalidate_caches()
    
    def _compute_distances(self):
        """Compute distances to all anchors."""
        for name, anchor in self.anchors.items():
            anchor_value = anchor.current_value
            
            if isinstance(self.value, (int, float)) and isinstance(anchor_value, (int, float)):
                self._distances[name] = abs(float(self.value) - float(anchor_value))
            else:
                # For non-numeric types, use custom distance
                self._distances[name] = self._compute_custom_distance(anchor_value)
    
    def _compute_custom_distance(self, anchor_value: Any) -> float:
        """
        Compute distance for non-numeric types.
        
        Override this in subclasses for custom distance metrics.
        """
        return 0.0
    
    def _invalidate_caches(self):
        """Invalidate all cached computations."""
        self._significance_cache.clear()
        self._qualifier_cache.clear()
    
    def update_value(self, new_value: Any):
        """
        Update relation value and recompute relationships.
        
        Args:
            new_value: New value for this relation
        """
        self.value = new_value
        self._compute_distances()
        self._invalidate_caches()
    
    def relation_to(self, anchor_name: str) -> str:
        """
        Get human-readable relation to an anchor.
        
        Args:
            anchor_name: Name of anchor to relate to
            
        Returns:
            Human-readable description like "17.7 over optimal"
            
        Raises:
            AnchorNotFoundError: If anchor doesn't exist
        """
        if anchor_name not in self.anchors:
            raise AnchorNotFoundError(anchor_name)
        
        anchor = self.anchors[anchor_name]
        anchor_value = anchor.current_value
        distance = self._distances[anchor_name]
        
        if isinstance(self.value, (int, float)) and isinstance(anchor_value, (int, float)):
            if self.value > anchor_value:
                return f"{distance:.2f} over {anchor_name}"
            elif self.value < anchor_value:
                return f"{distance:.2f} under {anchor_name}"
            else:
                return f"equal to {anchor_name}"
        
        # Non-numeric relation
        return f"related to {anchor_name}"
    
    def qualifier_to(self, anchor_name: str) -> RelationQualifier:
        """
        Get relational qualifier for an anchor.
        
        Args:
            anchor_name: Name of anchor to qualify against
            
        Returns:
            RelationQualifier enum describing the relationship
        """
        if anchor_name in self._qualifier_cache:
            return self._qualifier_cache[anchor_name]
        
        if anchor_name not in self.anchors:
            raise AnchorNotFoundError(anchor_name)
        
        anchor = self.anchors[anchor_name]
        anchor_value = anchor.current_value
        distance = self._distances[anchor_name]
        
        # Determine qualifier based on distance and tolerance
        if not isinstance(self.value, (int, float)):
            qualifier = RelationQualifier.APPROXIMATELY
        elif distance == 0:
            qualifier = RelationQualifier.EQUAL_TO
        elif distance <= anchor.tolerance:
            qualifier = RelationQualifier.APPROXIMATELY
        elif distance <= anchor.tolerance * 2:
            qualifier = RelationQualifier.NEAR
        elif distance <= anchor.tolerance * 5:
            if self.value > anchor_value:
                qualifier = RelationQualifier.OVER
            else:
                qualifier = RelationQualifier.UNDER
        else:
            qualifier = RelationQualifier.FAR_FROM
        
        self._qualifier_cache[anchor_name] = qualifier
        return qualifier
    
    def significance_to(self, anchor_name: str) -> RelationSignificance:
        """
        Determine significance of relation to anchor.
        
        Significance is based on distance relative to tolerance:
        - NEGLIGIBLE: Within 10% of tolerance
        - NOTICEABLE: Within tolerance
        - SIGNIFICANT: Within 2x tolerance
        - CRITICAL: Within 5x tolerance
        - EXTREME: Beyond 5x tolerance
        
        Args:
            anchor_name: Name of anchor to check significance against
            
        Returns:
            RelationSignificance enum
        """
        if anchor_name in self._significance_cache:
            return self._significance_cache[anchor_name]
        
        if anchor_name not in self.anchors:
            return RelationSignificance.NEGLIGIBLE
        
        anchor = self.anchors[anchor_name]
        distance = self._distances[anchor_name]
        tolerance = max(anchor.tolerance, 0.01)  # Avoid division by zero
        
        # Determine significance based on tolerance multiples
        ratio = distance / tolerance
        
        if ratio <= 0.1:
            significance = RelationSignificance.NEGLIGIBLE
        elif ratio <= 1.0:
            significance = RelationSignificance.NOTICEABLE
        elif ratio <= 2.0:
            significance = RelationSignificance.SIGNIFICANT
        elif ratio <= 5.0:
            significance = RelationSignificance.CRITICAL
        else:
            significance = RelationSignificance.EXTREME
        
        self._significance_cache[anchor_name] = significance
        return significance
    
    def is_approaching(self, anchor_name: str, threshold: float = 0.8) -> bool:
        """
        Check if value is approaching anchor.
        
        "Approaching" means within (threshold * tolerance) of the anchor.
        
        Args:
            anchor_name: Name of anchor to check
            threshold: Fraction of tolerance to use (0.0 to 1.0)
            
        Returns:
            True if approaching, False otherwise
        """
        if anchor_name not in self.anchors:
            return False
        
        anchor = self.anchors[anchor_name]
        distance = self._distances[anchor_name]
        
        return distance <= anchor.tolerance * threshold
    
    def is_over(self, anchor_name: str) -> bool:
        """Check if value is over (greater than) the anchor."""
        if anchor_name not in self.anchors:
            return False
        
        anchor = self.anchors[anchor_name]
        anchor_value = anchor.current_value
        
        if isinstance(self.value, (int, float)) and isinstance(anchor_value, (int, float)):
            return self.value > anchor_value
        
        return False
    
    def is_under(self, anchor_name: str) -> bool:
        """Check if value is under (less than) the anchor."""
        if anchor_name not in self.anchors:
            return False
        
        anchor = self.anchors[anchor_name]
        anchor_value = anchor.current_value
        
        if isinstance(self.value, (int, float)) and isinstance(anchor_value, (int, float)):
            return self.value < anchor_value
        
        return False
    
    def is_within_range(self, anchor_name: str, use_buffer: bool = True) -> bool:
        """
        Check if value is within anchor's acceptable range.
        
        Args:
            anchor_name: Name of anchor with range definition
            use_buffer: Whether to include buffer zone
            
        Returns:
            True if within range, False otherwise
        """
        if anchor_name not in self.anchors:
            return False
        
        anchor = self.anchors[anchor_name]
        
        if isinstance(self.value, (int, float)):
            return anchor.is_within_range(self.value, use_buffer)
        
        return False
    
    def suggested_actions(self) -> List[Dict[str, Any]]:
        """
        Generate suggested actions based on all anchor relationships.
        
        Analyzes relationships to all anchors and suggests actions
        when significant deviations are detected.
        
        Returns:
            List of action dictionaries with type, target, amount, priority, reason
        """
        actions = []
        
        for anchor_name, anchor in self.anchors.items():
            significance = self.significance_to(anchor_name)
            
            # Only suggest actions for significant deviations
            if significance < RelationSignificance.SIGNIFICANT:
                continue
            
            relation = self.relation_to(anchor_name)
            distance = self._distances[anchor_name]
            
            # Determine action type and priority
            if self.is_over(anchor_name):
                action_type = "reduce"
                direction = "over"
            elif self.is_under(anchor_name):
                action_type = "increase"
                direction = "under"
            else:
                continue
            
            # Map significance to priority
            priority_map = {
                RelationSignificance.SIGNIFICANT: PriorityLevel.NORMAL,
                RelationSignificance.CRITICAL: PriorityLevel.HIGH,
                RelationSignificance.EXTREME: PriorityLevel.CRITICAL
            }
            
            priority = priority_map.get(significance, PriorityLevel.NORMAL)
            
            action = {
                "type": action_type,
                "target": anchor_name,
                "amount": distance,
                "priority": priority,
                "reason": f"Value is {relation}",
                "significance": significance,
                "qualifier": self.qualifier_to(anchor_name)
            }
            
            actions.append(action)
        
        # Sort by priority (highest first)
        actions.sort(key=lambda a: a["priority"].numeric_value, reverse=True)
        
        return actions
    
    def get_expression(self) -> str:
        """
        Get a natural language expression of this relation.
        
        Returns:
            Human-readable description of all relationships
        """
        if not self.anchors:
            return f"value: {self.value}"
        
        relations = [self.relation_to(name) for name in self.anchors.keys()]
        return f"{self.value} ({', '.join(relations)})"
    
    def __repr__(self) -> str:
        """String representation for debugging."""
        return f"Relation({self.value}, {len(self.anchors)} anchors)"
    
    def __str__(self) -> str:
        """Human-readable string representation."""
        return self.get_expression()
