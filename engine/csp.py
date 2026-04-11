from dataclasses import dataclass
from typing import List, Dict, Tuple, Any, Callable
import random

@dataclass
class Variable:
    id: str
    section_id: int
    section_name: str
    subject: dict
    teacher_id: int
    duration: int
    student_count: int
    group: str = None
    difficulty: int = 1

class Constraint:
    """Base class for all constraints."""
    def __init__(self, variables: List[str]):
        self.variables = variables

    def is_satisfied(self, assignment: Dict[str, Tuple[str, int, dict]], csp_state: Any) -> bool:
        return True

class CSP:
    def __init__(self, variables: List[Variable], domains: Dict[str, List[Tuple[str, int, dict]]], state: Any):
        self.variables = variables
        self.domains = domains
        self.state = state
        self.constraints: Dict[str, List[Constraint]] = {var.id: [] for var in self.variables}
        
        # Dependency Map for Targeted Pruning
        self.neighbors: Dict[str, List[str]] = {var.id: [] for var in self.variables}
        self._build_neighbors()

        self.apply_assignment_hook: Callable[[Variable, Tuple[str, int, dict]], None] = None
        self.remove_assignment_hook: Callable[[Variable, Tuple[str, int, dict]], None] = None
        self.score_value_hook: Callable[[Variable, Tuple[str, int, dict]], int] = None

    def _build_neighbors(self):
        """Pre-calculate variables that share teacher, section, or room."""
        for i, v1 in enumerate(self.variables):
            for v2 in self.variables[i+1:]:
                # If they share teacher or section, they are neighbors (cannot be at same time)
                if v1.teacher_id == v2.teacher_id or v1.section_id == v2.section_id:
                    self.neighbors[v1.id].append(v2.id)
                    self.neighbors[v2.id].append(v1.id)

    def add_constraint(self, constraint: Constraint):
        for var_id in constraint.variables:
            if var_id in self.constraints:
                self.constraints[var_id].append(constraint)

    def is_consistent(self, var: Variable, value: Tuple[str, int, dict], assignment: Dict[str, Tuple[str, int, dict]]) -> bool:
        assignment[var.id] = value
        for constraint in self.constraints[var.id]:
            if not constraint.is_satisfied(assignment, self.state):
                del assignment[var.id]
                return False
        del assignment[var.id]
        return True

    def select_unassigned_variable(self, assignment: Dict[str, Tuple[str, int, dict]]) -> Variable:
        unassigned = [v for v in self.variables if v.id not in assignment]
        # MRV: sort by difficulty (desc) then domain size (asc)
        unassigned.sort(key=lambda v: (-v.difficulty, len(self.domains[v.id])))
        return unassigned[0]

    def order_domain_values(self, var: Variable, assignment: Dict[str, Tuple[str, int, dict]]) -> List[Tuple[str, int, dict]]:
        valid_values = []
        for val in self.domains[var.id]:
            if self.is_consistent(var, val, assignment):
                valid_values.append(val)
                
        if not valid_values: return []
            
        if self.score_value_hook:
            valid_values.sort(key=lambda val: self.score_value_hook(var, val), reverse=True)
        else:
            random.shuffle(valid_values)
        return valid_values

    def backtrack(self, assignment: Dict[str, Tuple[str, int, dict]], max_steps: int = 5000) -> Dict[str, Tuple[str, int, dict]]:
        if not hasattr(self, 'steps_taken'): self.steps_taken = 0
        self.steps_taken += 1
        if self.steps_taken > max_steps: return None 
            
        if len(assignment) == len(self.variables): return assignment

        var = self.select_unassigned_variable(assignment)
        ordered_values = self.order_domain_values(var, assignment)
        
        for value in ordered_values:
            if self.apply_assignment_hook: self.apply_assignment_hook(var, value)
            assignment[var.id] = value
            
            # --- TARGETED FORWARD CHECKING ---
            saved_domains = {}
            consistent = True
            
            # Only prune neighbors of the current variable
            for neighbor_id in self.neighbors[var.id]:
                if neighbor_id not in assignment:
                    saved_domains[neighbor_id] = list(self.domains[neighbor_id])
                    self.domains[neighbor_id] = [
                        val for val in self.domains[neighbor_id] 
                        if self.is_consistent(self._get_var(neighbor_id), val, assignment)
                    ]
                    if not self.domains[neighbor_id]:
                        consistent = False
                        break
            
            if consistent:
                result = self.backtrack(assignment, max_steps)
                if result is not None: return result
            
            # --- BACKTRACK ---
            for v_id, domain in saved_domains.items():
                self.domains[v_id] = domain
                
            del assignment[var.id]
            if self.remove_assignment_hook: self.remove_assignment_hook(var, value)
                
        return None

    def _get_var(self, var_id):
        for v in self.variables:
            if v.id == var_id: return v
        return None
