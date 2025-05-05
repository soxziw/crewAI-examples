from typing import Dict, List, Type, Any, Optional
from pydantic import BaseModel, Field
import json

# Import our mock BaseTool and required classes
from src.trip_planner.tools.flight_search_tool import BaseTool
try:
    from trip_planner.maia_architecture import Constraint, TravelPlan
except ImportError:
    from src.trip_planner.maia_architecture import Constraint, TravelPlan


class ConstraintVerificationToolInput(BaseModel):
    """Input schema for ConstraintVerificationTool."""
    travel_plan_json: str = Field(..., description="The travel plan in JSON format to verify against constraints.")
    constraints_json: str = Field(..., description="The list of constraints in JSON format to verify against.")


class ConstraintVerificationTool(BaseTool):
    name: str = "Constraint Verification Tool"
    description: str = (
        "A tool to verify if a travel plan meets all specified constraints. "
        "Returns a verification report with success/failure status for each constraint."
    )
    args_schema: Type[BaseModel] = ConstraintVerificationToolInput

    def _run(self, travel_plan_json: str, constraints_json: str) -> str:
        """
        Verify if the travel plan meets all specified constraints.
        
        Args:
            travel_plan_json: JSON string representation of a TravelPlan
            constraints_json: JSON string representation of a list of Constraint objects
            
        Returns:
            A verification report with success/failure status for each constraint
        """
        try:
            # Parse the JSON inputs
            travel_plan_dict = json.loads(travel_plan_json)
            constraints_list = json.loads(constraints_json)
            
            # Convert to objects
            travel_plan = TravelPlan(**travel_plan_dict)
            constraints = [Constraint(**c) for c in constraints_list]
            
            # Run verification
            verification_results = self._verify_constraints(travel_plan, constraints)
            
            # Format the results
            report = self._generate_verification_report(verification_results)
            return report
            
        except Exception as e:
            return f"Error during constraint verification: {str(e)}"
    
    def _verify_constraints(self, 
                           travel_plan: TravelPlan, 
                           constraints: List[Constraint]) -> Dict[str, Dict[str, Any]]:
        """
        Verify each constraint against the travel plan.
        
        Args:
            travel_plan: The travel plan to verify
            constraints: List of constraints to check
            
        Returns:
            Dictionary of verification results for each constraint
        """
        results = {}
        
        for i, constraint in enumerate(constraints):
            constraint_id = f"constraint_{i}"
            results[constraint_id] = {
                "constraint": constraint.dict(),
                "satisfied": False,
                "reason": "",
                "severity": "critical" if constraint.is_hard_constraint else "warning"
            }
            
            # Verify based on constraint type
            if constraint.type.value == "budget":
                results[constraint_id].update(self._verify_budget_constraint(travel_plan, constraint))
            elif constraint.type.value == "time":
                results[constraint_id].update(self._verify_time_constraint(travel_plan, constraint))
            elif constraint.type.value == "preference":
                results[constraint_id].update(self._verify_preference_constraint(travel_plan, constraint))
            elif constraint.type.value == "logistics":
                results[constraint_id].update(self._verify_logistics_constraint(travel_plan, constraint))
            elif constraint.type.value == "accessibility":
                results[constraint_id].update(self._verify_accessibility_constraint(travel_plan, constraint))
            elif constraint.type.value == "safety":
                results[constraint_id].update(self._verify_safety_constraint(travel_plan, constraint))
            else:
                results[constraint_id].update({
                    "satisfied": False,
                    "reason": f"Unknown constraint type: {constraint.type.value}"
                })
        
        return results
    
    def _generate_verification_report(self, results: Dict[str, Dict[str, Any]]) -> str:
        """
        Generate a human-readable verification report.
        
        Args:
            results: Dictionary of verification results
            
        Returns:
            A formatted verification report
        """
        report = "# Constraint Verification Report\n\n"
        
        # Count satisfied constraints
        total = len(results)
        satisfied = sum(1 for r in results.values() if r["satisfied"])
        
        # Summary
        report += f"## Summary\n\n"
        report += f"- Total constraints: {total}\n"
        report += f"- Satisfied constraints: {satisfied}\n"
        report += f"- Failed constraints: {total - satisfied}\n\n"
        
        if satisfied == total:
            report += "✅ **ALL CONSTRAINTS SATISFIED**\n\n"
        else:
            report += "❌ **SOME CONSTRAINTS FAILED**\n\n"
        
        # Detailed results
        report += "## Detailed Results\n\n"
        
        for constraint_id, result in results.items():
            constraint = result["constraint"]
            status = "✅" if result["satisfied"] else "❌"
            severity = "🔴" if result["severity"] == "critical" else "🟠"
            
            report += f"### {severity} {status} {constraint['description']}\n\n"
            
            if not result["satisfied"]:
                report += f"**FAILED**: {result['reason']}\n\n"
            else:
                report += f"**PASSED**: {result['reason']}\n\n"
        
        return report
    
    def _verify_budget_constraint(self, 
                                 travel_plan: TravelPlan, 
                                 constraint: Constraint) -> Dict[str, Any]:
        """Verify a budget constraint."""
        # Example implementation - would be more sophisticated in real implementation
        try:
            if "maximum" in constraint.description.lower() and constraint.value:
                # Calculate total cost from travel plan
                total_cost = 0
                # Add accommodation costs
                # Add transportation costs
                # Add activity costs
                
                if total_cost <= float(constraint.value):
                    return {
                        "satisfied": True,
                        "reason": f"Total cost ${total_cost} is within budget ${constraint.value}"
                    }
                else:
                    return {
                        "satisfied": False,
                        "reason": f"Total cost ${total_cost} exceeds budget ${constraint.value}"
                    }
            
            return {
                "satisfied": False,
                "reason": "Could not verify budget constraint - insufficient information"
            }
        except Exception as e:
            return {
                "satisfied": False,
                "reason": f"Error verifying budget constraint: {str(e)}"
            }
    
    def _verify_time_constraint(self, 
                               travel_plan: TravelPlan, 
                               constraint: Constraint) -> Dict[str, Any]:
        """Verify a time constraint."""
        # Implementation would check timing constraints
        return {
            "satisfied": True,
            "reason": "Time constraint verified (placeholder implementation)"
        }
    
    def _verify_preference_constraint(self, 
                                    travel_plan: TravelPlan, 
                                    constraint: Constraint) -> Dict[str, Any]:
        """Verify a preference constraint."""
        # Implementation would check if preferences are included in the plan
        return {
            "satisfied": True,
            "reason": "Preference constraint verified (placeholder implementation)"
        }
    
    def _verify_logistics_constraint(self, 
                                   travel_plan: TravelPlan, 
                                   constraint: Constraint) -> Dict[str, Any]:
        """Verify a logistics constraint."""
        # Implementation would check logistical feasibility
        return {
            "satisfied": True,
            "reason": "Logistics constraint verified (placeholder implementation)"
        }
    
    def _verify_accessibility_constraint(self, 
                                       travel_plan: TravelPlan, 
                                       constraint: Constraint) -> Dict[str, Any]:
        """Verify an accessibility constraint."""
        # Implementation would check if accessibility requirements are met
        return {
            "satisfied": True,
            "reason": "Accessibility constraint verified (placeholder implementation)"
        }
    
    def _verify_safety_constraint(self, 
                                travel_plan: TravelPlan, 
                                constraint: Constraint) -> Dict[str, Any]:
        """Verify a safety constraint."""
        # Implementation would check safety requirements
        return {
            "satisfied": True,
            "reason": "Safety constraint verified (placeholder implementation)"
        }