"""
Constraint Management System for MAIA

This module provides a comprehensive constraint management system that:
1. Stores and tracks constraints throughout the planning process
2. Verifies constraints at each planning layer
3. Provides feedback on constraint violations
4. Handles replanning when constraints are violated
"""

import json
from typing import Dict, List, Optional, Any, Union, Callable
from enum import Enum

try:
    # When installed as a package
    from trip_planner.maia_architecture import (
        Constraint, 
        TravelPlan, 
        AgentLayer,
        PlanningState
    )
except ImportError:
    # When running directly from source
    from src.trip_planner.maia_architecture import (
        Constraint, 
        TravelPlan, 
        AgentLayer,
        PlanningState
    )


class VerificationResult(Enum):
    """Results of constraint verification."""
    PASSED = "passed"
    FAILED_RECOVERABLE = "failed_recoverable"
    FAILED_CRITICAL = "failed_critical"


class ConstraintViolation:
    """Represents a constraint violation."""
    
    def __init__(self, constraint: Constraint, reason: str):
        self.constraint = constraint
        self.reason = reason
        self.severity = "critical" if constraint.is_hard_constraint else "warning"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "constraint": self.constraint.dict(),
            "reason": self.reason,
            "severity": self.severity
        }
    
    def __str__(self) -> str:
        return f"{'CRITICAL' if self.severity == 'critical' else 'WARNING'}: {self.constraint.description} - {self.reason}"


class LayerVerificationResult:
    """Results of verification for a specific layer."""
    
    def __init__(
        self, 
        layer: AgentLayer,
        passed: bool,
        violations: List[ConstraintViolation] = None,
        result_type: VerificationResult = None
    ):
        self.layer = layer
        self.passed = passed
        self.violations = violations or []
        self.result_type = result_type or (
            VerificationResult.PASSED if passed 
            else VerificationResult.FAILED_CRITICAL
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "layer": self.layer.value,
            "passed": self.passed,
            "result_type": self.result_type.value,
            "violations": [v.to_dict() for v in self.violations]
        }
    
    def __str__(self) -> str:
        if self.passed:
            return f"Layer {self.layer.value}: ALL CONSTRAINTS PASSED"
        else:
            return f"Layer {self.layer.value}: {len(self.violations)} CONSTRAINT VIOLATIONS"


class ConstraintManager:
    """
    Manager for storing, tracking, and verifying constraints throughout 
    the planning process.
    """
    
    def __init__(self):
        self.constraints: List[Constraint] = []
        self.layer_constraints: Dict[str, List[Constraint]] = {
            layer.value: [] for layer in AgentLayer
        }
        self.verification_results: Dict[str, LayerVerificationResult] = {}
        self.verification_callbacks: Dict[str, List[Callable]] = {}
    
    def add_constraints(self, constraints: List[Constraint]) -> None:
        """
        Add constraints to the manager and assign them to appropriate layers.
        
        Args:
            constraints: List of constraints to add
        """
        self.constraints.extend(constraints)
        
        # Assign constraints to layers
        for constraint in constraints:
            if constraint.layer:
                self.layer_constraints[constraint.layer].append(constraint)
            else:
                # Default to verification layer for unassigned constraints
                self.layer_constraints[AgentLayer.VERIFICATION.value].append(constraint)
    
    def get_constraints_for_layer(self, layer: Union[AgentLayer, str]) -> List[Constraint]:
        """
        Get all constraints applicable to a specific layer.
        
        Args:
            layer: The layer to get constraints for
            
        Returns:
            List of constraints for the specified layer
        """
        layer_key = layer.value if isinstance(layer, AgentLayer) else layer
        return self.layer_constraints.get(layer_key, [])
    
    def register_verification_callback(
        self, 
        layer: Union[AgentLayer, str], 
        callback: Callable[[LayerVerificationResult], None]
    ) -> None:
        """
        Register a callback to be called when verification for a layer completes.
        
        Args:
            layer: The layer to register the callback for
            callback: The callback function to register
        """
        layer_key = layer.value if isinstance(layer, AgentLayer) else layer
        
        if layer_key not in self.verification_callbacks:
            self.verification_callbacks[layer_key] = []
            
        self.verification_callbacks[layer_key].append(callback)
    
    def verify_layer(
        self, 
        layer: Union[AgentLayer, str], 
        travel_plan: TravelPlan,
        custom_verifier: Optional[Callable[[TravelPlan, List[Constraint]], List[ConstraintViolation]]] = None
    ) -> LayerVerificationResult:
        """
        Verify all constraints for a specific layer against the travel plan.
        
        Args:
            layer: The layer to verify constraints for
            travel_plan: The travel plan to verify against
            custom_verifier: Optional custom verification function
            
        Returns:
            Verification result for the layer
        """
        layer_key = layer.value if isinstance(layer, AgentLayer) else layer
        constraints = self.get_constraints_for_layer(layer_key)
        
        # No constraints to verify
        if not constraints:
            result = LayerVerificationResult(
                layer=AgentLayer(layer_key),
                passed=True,
                result_type=VerificationResult.PASSED
            )
            self.verification_results[layer_key] = result
            return result
        
        # Use custom verifier if provided, otherwise use default
        violations = (
            custom_verifier(travel_plan, constraints) 
            if custom_verifier 
            else self._default_verify(travel_plan, constraints)
        )
        
        # Check if any critical constraints were violated
        critical_violations = [v for v in violations if v.severity == "critical"]
        passed = len(violations) == 0
        
        result_type = VerificationResult.PASSED
        if not passed:
            result_type = (
                VerificationResult.FAILED_CRITICAL 
                if critical_violations 
                else VerificationResult.FAILED_RECOVERABLE
            )
        
        result = LayerVerificationResult(
            layer=AgentLayer(layer_key),
            passed=passed,
            violations=violations,
            result_type=result_type
        )
        
        # Store the result
        self.verification_results[layer_key] = result
        
        # Call any registered callbacks
        for callback in self.verification_callbacks.get(layer_key, []):
            callback(result)
        
        return result
    
    def _default_verify(
        self, 
        travel_plan: TravelPlan, 
        constraints: List[Constraint]
    ) -> List[ConstraintViolation]:
        """
        Default verification function for constraints.
        
        Args:
            travel_plan: The travel plan to verify
            constraints: The constraints to verify
            
        Returns:
            List of constraint violations
        """
        violations = []
        
        for constraint in constraints:
            # Implement verification logic for each constraint type
            if constraint.type.value == "budget":
                # Example budget verification
                if "maximum" in constraint.description.lower() and constraint.value:
                    # Calculate total cost from travel plan (simplified example)
                    total_cost = 0
                    if hasattr(travel_plan, 'accommodations') and travel_plan.accommodations:
                        # Sum accommodation costs (simplified)
                        for city, options in travel_plan.accommodations.items():
                            for option in options:
                                if 'price' in option:
                                    total_cost += float(option['price'].replace('$', '').replace(',', ''))
                    
                    if total_cost > float(constraint.value):
                        violations.append(ConstraintViolation(
                            constraint=constraint,
                            reason=f"Total cost ${total_cost} exceeds budget ${constraint.value}"
                        ))
            
            # Add verification for other constraint types here
        
        return violations
    
    def all_constraints_satisfied(self) -> bool:
        """
        Check if all constraints have been satisfied.
        
        Returns:
            True if all constraints are satisfied, False otherwise
        """
        return all(result.passed for result in self.verification_results.values())
    
    def get_all_violations(self) -> List[ConstraintViolation]:
        """
        Get all constraint violations across all layers.
        
        Returns:
            List of all constraint violations
        """
        all_violations = []
        for result in self.verification_results.values():
            all_violations.extend(result.violations)
        return all_violations
    
    def generate_verification_report(self) -> str:
        """
        Generate a human-readable verification report.
        
        Returns:
            Formatted verification report
        """
        report = "# MAIA Constraint Verification Report\n\n"
        
        # Count satisfied constraints
        total = len(self.constraints)
        violations = self.get_all_violations()
        satisfied = total - len(violations)
        
        # Summary
        report += f"## Summary\n\n"
        report += f"- Total constraints: {total}\n"
        report += f"- Satisfied constraints: {satisfied}\n"
        report += f"- Failed constraints: {len(violations)}\n\n"
        
        if len(violations) == 0:
            report += "✅ **ALL CONSTRAINTS SATISFIED**\n\n"
        else:
            report += "❌ **SOME CONSTRAINTS FAILED**\n\n"
        
        # Results by layer
        report += "## Results by Layer\n\n"
        
        for layer_key, result in self.verification_results.items():
            status = "✅" if result.passed else "❌"
            report += f"### {status} {layer_key.capitalize()} Layer\n\n"
            
            if result.passed:
                report += f"All constraints for this layer are satisfied.\n\n"
            else:
                report += f"**{len(result.violations)} violations detected:**\n\n"
                for violation in result.violations:
                    severity = "🔴" if violation.severity == "critical" else "🟠"
                    report += f"- {severity} {violation.constraint.description}: {violation.reason}\n"
                report += "\n"
        
        # Detailed failures
        if violations:
            report += "## Critical Violations\n\n"
            critical_violations = [v for v in violations if v.severity == "critical"]
            
            if critical_violations:
                for violation in critical_violations:
                    report += f"### 🔴 {violation.constraint.description}\n\n"
                    report += f"**Reason**: {violation.reason}\n\n"
            else:
                report += "No critical violations detected.\n\n"
        
        return report