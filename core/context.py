"""
YHWH Language - Relational Context Manager
Genesis 1:1 - In the beginning...

Manages anchors, relations, and execution context for relational programs.
"""
from typing import Dict, List, Any, Optional
from .anchors import Anchor, AnchorRegistry
from .relations import Relation
from .types import RelationSignificance, PriorityLevel
from .exceptions import AnchorNotFoundError, ContextError


class RelationalContext:
    """
    Manages anchors and relationships in execution context.
    
    The RelationalContext is the runtime environment for relational
    programs. It tracks all anchors, relational variables, and provides
    facilities for evaluating relational conditions and generating
    explanations.
    
    Attributes:
        anchors: Registry of all defined anchors
        variables: Dictionary of relational variables
        context_stack: Stack for nested contexts (scopes)
        metadata: Context-wide configuration and state
    """
    
    def __init__(self):
        self.anchor_registry = AnchorRegistry()
        self.variables: Dict[str, Relation] = {}
        self.context_stack: List[Dict[str, Any]] = []
        self.metadata: Dict[str, Any] = {
            "optimization_goals": {},
            "explanation_mode": True,
            "confidence_threshold": 0.8,
            "significance_threshold": RelationSignificance.SIGNIFICANT,
            "auto_suggest_actions": True
        }
        
        # Execution tracking
        self._execution_log: List[Dict[str, Any]] = []
        self._decision_history: List[Dict[str, Any]] = []
    
    def add_anchor(self, anchor: Anchor):
        """
        Add an anchor to the context.
        
        Args:
            anchor: Anchor instance to register
        """
        self.anchor_registry.register(anchor)
        
        # Update all existing relations that reference this anchor
        for var_name, relation in self.variables.items():
            if anchor.name in relation.anchors:
                # Update anchor reference and recompute
                relation.anchors[anchor.name] = anchor
                relation._compute_distances()
                relation._invalidate_caches()
    
    def get_anchor(self, name: str) -> Anchor:
        """
        Get an anchor by name.
        
        Args:
            name: Anchor name
            
        Returns:
            Anchor instance
            
        Raises:
            AnchorNotFoundError: If anchor doesn't exist
        """
        anchor = self.anchor_registry.get(name)
        if anchor is None:
            raise AnchorNotFoundError(name)
        return anchor
    
    def has_anchor(self, name: str) -> bool:
        """Check if an anchor exists in context."""
        return self.anchor_registry.get(name) is not None
    
    def create_relation(
        self, 
        name: str, 
        value: Any, 
        anchor_names: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Relation:
        """
        Create a new relational variable.
        
        Args:
            name: Variable name
            value: Initial value
            anchor_names: List of anchor names to relate to (if None, auto-detect)
            metadata: Optional metadata for the relation
            
        Returns:
            Created Relation instance
        """
        if anchor_names is None:
            # Auto-detect relevant anchors based on type and context
            anchor_names = self._find_relevant_anchors(value)
        
        # Build anchors dictionary
        anchors = {}
        for anchor_name in anchor_names:
            if self.has_anchor(anchor_name):
                anchors[anchor_name] = self.get_anchor(anchor_name)
        
        # Create relation
        relation = Relation(
            value=value,
            anchors=anchors,
            metadata=metadata or {}
        )
        
        # Store in context
        self.variables[name] = relation
        
        # Log creation
        if self.metadata["explanation_mode"]:
            self._log_event({
                "type": "relation_created",
                "name": name,
                "value": value,
                "anchors": list(anchors.keys()),
                "expression": relation.get_expression()
            })
        
        return relation
    
    def update_relation(self, name: str, new_value: Any):
        """
        Update a relational variable's value.
        
        Args:
            name: Variable name
            new_value: New value
            
        Raises:
            ContextError: If variable doesn't exist
        """
        if name not in self.variables:
            raise ContextError(f"Variable '{name}' not found in context")
        
        old_value = self.variables[name].value
        self.variables[name].update_value(new_value)
        
        # Log update
        if self.metadata["explanation_mode"]:
            self._log_event({
                "type": "relation_updated",
                "name": name,
                "old_value": old_value,
                "new_value": new_value,
                "expression": self.variables[name].get_expression()
            })
    
    def get_relation(self, name: str) -> Relation:
        """
        Get a relational variable.
        
        Args:
            name: Variable name
            
        Returns:
            Relation instance
            
        Raises:
            ContextError: If variable doesn't exist
        """
        if name not in self.variables:
            raise ContextError(f"Variable '{name}' not found in context")
        return self.variables[name]
    
    def _find_relevant_anchors(self, value: Any) -> List[str]:
        """
        Find anchors relevant to a given value based on type and context.
        
        Args:
            value: Value to find anchors for
            
        Returns:
            List of relevant anchor names
        """
        relevant = []
        
        # Type-based matching
        value_type = type(value)
        type_matching_anchors = self.anchor_registry.find_by_type(value_type)
        relevant.extend([a.name for a in type_matching_anchors])
        
        # Context-based matching (if current context is set)
        if self.context_stack:
            current_context = self.context_stack[-1].get("context", "default")
            context_anchors = self.anchor_registry.find_by_context(current_context)
            relevant.extend([a.name for a in context_anchors if a.name not in relevant])
        
        return relevant
    
    def evaluate_condition(self, relation_name: str, qualifier: str, anchor_name: str) -> bool:
        """
        Evaluate a relational condition.
        
        Args:
            relation_name: Name of relational variable
            qualifier: Relational qualifier (over, under, approaching, etc.)
            anchor_name: Name of anchor to compare against
            
        Returns:
            True if condition holds, False otherwise
        """
        try:
            relation = self.get_relation(relation_name)
            
            # Map qualifier to method
            qualifier_map = {
                "over": relation.is_over,
                "under": relation.is_under,
                "approaching": relation.is_approaching,
                "within": relation.is_within_range,
                "equal_to": lambda a: relation.qualifier_to(a).name == "EQUAL_TO",
                "near": lambda a: relation.qualifier_to(a).name == "NEAR",
            }
            
            if qualifier in qualifier_map:
                result = qualifier_map[qualifier](anchor_name)
                
                # Log evaluation
                if self.metadata["explanation_mode"]:
                    self._log_event({
                        "type": "condition_evaluated",
                        "relation": relation_name,
                        "qualifier": qualifier,
                        "anchor": anchor_name,
                        "result": result,
                        "expression": relation.get_expression()
                    })
                
                return result
            
            return False
            
        except Exception as e:
            if self.metadata["explanation_mode"]:
                self._log_event({
                    "type": "evaluation_error",
                    "relation": relation_name,
                    "error": str(e)
                })
            return False
    
    def get_suggested_actions(self, relation_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get suggested actions for one or all relations.
        
        Args:
            relation_name: Specific relation to get actions for (or None for all)
            
        Returns:
            List of suggested action dictionaries
        """
        all_actions = []
        
        if relation_name:
            # Get actions for specific relation
            if relation_name in self.variables:
                actions = self.variables[relation_name].suggested_actions()
                for action in actions:
                    action["relation"] = relation_name
                all_actions.extend(actions)
        else:
            # Get actions for all relations
            for var_name, relation in self.variables.items():
                actions = relation.suggested_actions()
                for action in actions:
                    action["relation"] = var_name
                all_actions.extend(actions)
        
        # Filter by significance threshold
        threshold = self.metadata["significance_threshold"]
        filtered_actions = [
            a for a in all_actions
            if a["significance"] >= threshold
        ]
        
        # Sort by priority
        filtered_actions.sort(key=lambda a: a["priority"].numeric_value, reverse=True)
        
        return filtered_actions
    
    def push_context(self, context_name: str, metadata: Optional[Dict] = None):
        """
        Push a new context onto the stack (for scoping).
        
        Args:
            context_name: Name of the new context
            metadata: Optional metadata for this context
        """
        self.context_stack.append({
            "name": context_name,
            "metadata": metadata or {},
            "variables": set()
        })
    
    def pop_context(self):
        """Pop the current context from the stack."""
        if not self.context_stack:
            raise ContextError("No context to pop")
        
        context = self.context_stack.pop()
        
        # Clean up variables from this context if needed
        # (for now, we keep them in the global namespace)
        
        return context
    
    def _log_event(self, event: Dict[str, Any]):
        """Log an execution event for debugging/explanation."""
        self._execution_log.append(event)
        
        # Keep log size manageable
        if len(self._execution_log) > 1000:
            self._execution_log = self._execution_log[-1000:]
    
    def get_execution_log(self, event_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get execution log, optionally filtered by event type.
        
        Args:
            event_type: Optional event type to filter by
            
        Returns:
            List of log events
        """
        if event_type:
            return [e for e in self._execution_log if e.get("type") == event_type]
        return self._execution_log.copy()
    
    def explain_state(self) -> str:
        """
        Generate a human-readable explanation of current state.
        
        Returns:
            Multi-line explanation of all relations and their states
        """
        lines = ["Current Relational State:", "=" * 50]
        
        if not self.variables:
            lines.append("No relational variables defined.")
            return "\n".join(lines)
        
        for var_name, relation in self.variables.items():
            lines.append(f"\n{var_name}: {relation.get_expression()}")
            
            # Show significance for each anchor
            for anchor_name in relation.anchors.keys():
                significance = relation.significance_to(anchor_name)
                qualifier = relation.qualifier_to(anchor_name)
                lines.append(f"  → {anchor_name}: {significance.value} ({qualifier.value})")
            
            # Show suggested actions if any
            actions = relation.suggested_actions()
            if actions:
                lines.append(f"  Suggested actions:")
                for action in actions[:3]:  # Show top 3
                    lines.append(f"    - {action['type']} by {action['amount']:.2f} (priority: {action['priority'].value})")
        
        return "\n".join(lines)
    
    def update_dynamic_anchors(self):
        """Update all dynamic anchors and affected relations."""
        self.anchor_registry.update_dynamic_anchors()
        
        # Recompute all relations
        for relation in self.variables.values():
            relation._compute_distances()
            relation._invalidate_caches()
