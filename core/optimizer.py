"""
GIANT Language - Optimization Engine
Genesis 1:1 - In the beginning...

Multi-objective optimization for relational decision-making.
"""
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass
from .types import OptimizationGoal, PriorityLevel
from .context import RelationalContext
from .exceptions import OptimizationError


@dataclass
class Objective:
    """
    An optimization objective.
    
    Attributes:
        name: Objective identifier
        goal: MINIMIZE or MAXIMIZE
        weight: Relative importance (higher = more important)
        evaluator: Function to compute objective value from solution
    """
    name: str
    goal: OptimizationGoal
    weight: float = 1.0
    evaluator: Optional[Callable[[Dict], float]] = None


@dataclass
class Constraint:
    """
    An optimization constraint.
    
    Attributes:
        name: Constraint identifier
        validator: Function that returns True if constraint satisfied
        penalty: Penalty value for violating this constraint
        description: Human-readable description
    """
    name: str
    validator: Callable[[Dict], bool]
    penalty: float = 1000.0
    description: str = ""


class OptimizationEngine:
    """
    Handles multi-objective optimization for relational decisions.
    
    The optimization engine helps choose between competing actions
    when multiple relational conditions trigger simultaneously.
    
    It supports:
    - Multiple conflicting objectives (minimize cost, maximize quality)
    - Weighted importance of objectives
    - Hard and soft constraints
    - Explanation of tradeoffs made
    """
    
    def __init__(self):
        self.objectives: Dict[str, Objective] = {}
        self.constraints: List[Constraint] = []
        self.solutions: List[Dict[str, Any]] = []
        self._evaluation_cache: Dict[str, float] = {}
    
    def add_objective(
        self, 
        name: str, 
        goal: OptimizationGoal,
        weight: float = 1.0,
        evaluator: Optional[Callable[[Dict], float]] = None
    ):
        """
        Add an optimization objective.
        
        Args:
            name: Objective identifier
            goal: MINIMIZE or MAXIMIZE
            weight: Relative importance (default 1.0)
            evaluator: Optional custom evaluation function
        """
        self.objectives[name] = Objective(
            name=name,
            goal=goal,
            weight=weight,
            evaluator=evaluator
        )
        
        # Clear cache when objectives change
        self._evaluation_cache.clear()
    
    def add_constraint(
        self,
        name: str,
        validator: Callable[[Dict], bool],
        penalty: float = 1000.0,
        description: str = ""
    ):
        """
        Add an optimization constraint.
        
        Args:
            name: Constraint identifier
            validator: Function that returns True if satisfied
            penalty: Penalty for violating constraint
            description: Human-readable description
        """
        self.constraints.append(Constraint(
            name=name,
            validator=validator,
            penalty=penalty,
            description=description or f"Constraint: {name}"
        ))
        
        # Clear cache when constraints change
        self._evaluation_cache.clear()
    
    def evaluate_solution(self, solution: Dict[str, Any]) -> float:
        """
        Evaluate a solution against all objectives and constraints.
        
        Args:
            solution: Dictionary containing solution parameters
            
        Returns:
            Overall score (higher is better)
        """
        # Check cache
        solution_key = self._solution_key(solution)
        if solution_key in self._evaluation_cache:
            return self._evaluation_cache[solution_key]
        
        score = 0.0
        
        # Evaluate each objective
        for obj_name, objective in self.objectives.items():
            try:
                if objective.evaluator:
                    # Use custom evaluator
                    value = objective.evaluator(solution)
                elif obj_name in solution:
                    # Use value from solution directly
                    value = float(solution[obj_name])
                else:
                    # Objective not applicable to this solution
                    continue
                
                weight = objective.weight
                
                if objective.goal == OptimizationGoal.MINIMIZE:
                    # Lower values are better for minimization
                    # Negate so higher score is still better
                    score -= value * weight
                else:  # MAXIMIZE
                    score += value * weight
                    
            except Exception as e:
                # Log error but continue
                print(f"Warning: Error evaluating objective {obj_name}: {e}")
        
        # Apply constraint penalties
        for constraint in self.constraints:
            try:
                if not constraint.validator(solution):
                    score -= constraint.penalty
            except Exception as e:
                # Treat evaluation error as constraint violation
                print(f"Warning: Error evaluating constraint {constraint.name}: {e}")
                score -= constraint.penalty
        
        # Cache result
        self._evaluation_cache[solution_key] = score
        
        return score
    
    def _solution_key(self, solution: Dict[str, Any]) -> str:
        """Generate a cache key for a solution."""
        # Sort keys for consistent hashing
        items = sorted(solution.items())
        return str(items)
    
    def find_optimal_action(
        self,
        context: RelationalContext,
        possible_actions: List[Dict[str, Any]]
    ) -> Optional[Dict[str, Any]]:
        """
        Find the optimal action given objectives and context.
        
        Args:
            context: Current relational context
            possible_actions: List of possible action dictionaries
            
        Returns:
            Optimal action dictionary, or None if no valid actions
        """
        if not possible_actions:
            return None
        
        scored_actions = []
        
        for action in possible_actions:
            try:
                # Simulate action outcome
                simulated_outcome = self._simulate_action(action, context)
                
                # Evaluate outcome
                score = self.evaluate_solution(simulated_outcome)
                
                scored_actions.append({
                    "action": action,
                    "score": score,
                    "outcome": simulated_outcome,
                    "explanation": self._explain_score(simulated_outcome, score)
                })
            except Exception as e:
                print(f"Warning: Error evaluating action: {e}")
                continue
        
        if not scored_actions:
            return None
        
        # Return action with highest score
        best = max(scored_actions, key=lambda x: x["score"])
        
        # Store for later analysis
        self.solutions.append(best)
        
        return best["action"]
    
    def _simulate_action(
        self,
        action: Dict[str, Any],
        context: RelationalContext
    ) -> Dict[str, Any]:
        """
        Simulate the outcome of an action.
        
        This is a simplified simulation. In a real system, this would
        involve more sophisticated modeling of system dynamics.
        
        Args:
            action: Action dictionary
            context: Current context
            
        Returns:
            Dictionary of predicted outcomes
        """
        action_type = action.get("type", "unknown")
        amount = action.get("amount", 0.0)
        priority = action.get("priority", PriorityLevel.NORMAL)
        
        # Simple heuristic-based simulation
        outcome = {
            "action_type": action_type,
            "amount": amount,
            "priority_value": priority.numeric_value if isinstance(priority, PriorityLevel) else 2
        }
        
        # Estimate impacts on common objectives
        if action_type == "reduce":
            outcome["energy_impact"] = -abs(amount) * 0.1
            outcome["cost"] = abs(amount) * 0.05
            outcome["safety_improvement"] = abs(amount) * 0.3
        elif action_type == "increase":
            outcome["energy_impact"] = abs(amount) * 0.15
            outcome["cost"] = abs(amount) * 0.08
            outcome["safety_improvement"] = -abs(amount) * 0.1
        else:
            outcome["energy_impact"] = 0.0
            outcome["cost"] = 0.0
            outcome["safety_improvement"] = 0.0
        
        # Priority affects how quickly action is taken
        outcome["response_time"] = 10.0 / outcome["priority_value"]
        
        return outcome
    
    def _explain_score(self, outcome: Dict[str, Any], score: float) -> str:
        """
        Generate explanation of how a score was computed.
        
        Args:
            outcome: Outcome dictionary
            score: Computed score
            
        Returns:
            Human-readable explanation
        """
        lines = [f"Overall score: {score:.2f}"]
        
        # Explain each objective's contribution
        for obj_name, objective in self.objectives.items():
            if obj_name in outcome:
                value = outcome[obj_name]
                contribution = value * objective.weight
                if objective.goal == OptimizationGoal.MINIMIZE:
                    contribution = -contribution
                
                lines.append(
                    f"  {obj_name}: {value:.2f} → "
                    f"{contribution:.2f} ({objective.goal.value})"
                )
        
        # Check constraint violations
        violated = []
        for constraint in self.constraints:
            if not constraint.validator(outcome):
                violated.append(constraint.name)
        
        if violated:
            lines.append(f"  Violated constraints: {', '.join(violated)}")
        
        return "\n".join(lines)
    
    def explain_tradeoffs(self) -> str:
        """
        Explain tradeoffs between objectives.
        
        Returns:
            Human-readable explanation of objective conflicts
        """
        if len(self.objectives) < 2:
            return "No tradeoffs (only one objective defined)"
        
        lines = ["Optimization Tradeoffs:", "=" * 50]
        
        # Identify conflicting objectives
        minimize_objs = [
            obj for obj in self.objectives.values()
            if obj.goal == OptimizationGoal.MINIMIZE
        ]
        maximize_objs = [
            obj for obj in self.objectives.values()
            if obj.goal == OptimizationGoal.MAXIMIZE
        ]
        
        if minimize_objs and maximize_objs:
            lines.append("\nConflicting objectives detected:")
            lines.append("  Minimizing: " + ", ".join(o.name for o in minimize_objs))
            lines.append("  Maximizing: " + ", ".join(o.name for o in maximize_objs))
        
        # Show weights
        lines.append("\nObjective weights (importance):")
        for obj in sorted(self.objectives.values(), key=lambda x: x.weight, reverse=True):
            lines.append(f"  {obj.name}: {obj.weight:.2f} ({obj.goal.value})")
        
        # Show constraints
        if self.constraints:
            lines.append(f"\nActive constraints: {len(self.constraints)}")
            for constraint in self.constraints:
                lines.append(f"  - {constraint.description}")
        
        return "\n".join(lines)
    
    def get_pareto_front(self) -> List[Dict[str, Any]]:
        """
        Get Pareto-optimal solutions from evaluated solutions.
        
        A solution is Pareto-optimal if no other solution is better
        in all objectives.
        
        Returns:
            List of Pareto-optimal solutions
        """
        if not self.solutions:
            return []
        
        pareto = []
        
        for candidate in self.solutions:
            is_dominated = False
            
            for other in self.solutions:
                if candidate == other:
                    continue
                
                # Check if other dominates candidate
                if self._dominates(other["outcome"], candidate["outcome"]):
                    is_dominated = True
                    break
            
            if not is_dominated:
                pareto.append(candidate)
        
        return pareto
    
    def _dominates(self, solution_a: Dict, solution_b: Dict) -> bool:
        """
        Check if solution A dominates solution B.
        
        A dominates B if A is better or equal in all objectives
        and strictly better in at least one.
        """
        better_in_any = False
        
        for obj_name, objective in self.objectives.items():
            if obj_name not in solution_a or obj_name not in solution_b:
                continue
            
            val_a = solution_a[obj_name]
            val_b = solution_b[obj_name]
            
            if objective.goal == OptimizationGoal.MINIMIZE:
                if val_a > val_b:  # A is worse
                    return False
                elif val_a < val_b:  # A is better
                    better_in_any = True
            else:  # MAXIMIZE
                if val_a < val_b:  # A is worse
                    return False
                elif val_a > val_b:  # A is better
                    better_in_any = True
        
        return better_in_any
