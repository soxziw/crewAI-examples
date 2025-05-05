from crewai.tools import BaseTool
from typing import Type, List
from pydantic import BaseModel, Field
import json
import re

from trip_planner.maia_architecture import Constraint, ConstraintType


class ConstraintParserToolInput(BaseModel):
    """Input schema for ConstraintParserTool."""
    user_request: str = Field(..., description="The user's travel request in natural language.")


class ConstraintParserTool(BaseTool):
    name: str = "Constraint Parser Tool"
    description: str = (
        "A tool to extract travel constraints from natural language user requests. "
        "Identifies and categorizes constraints related to budget, time, preferences, logistics, accessibility, and safety."
    )
    args_schema: Type[BaseModel] = ConstraintParserToolInput

    def _run(self, user_request: str) -> str:
        """
        Extract constraints from the user's natural language request.
        
        Args:
            user_request: The user's travel request
            
        Returns:
            JSON string of extracted constraints
        """
        try:
            # Extract constraints from the request
            constraints = self._extract_constraints(user_request)
            
            # Convert to JSON
            constraints_json = json.dumps([c.dict() for c in constraints], indent=2)
            
            # Return with a summary
            return (
                f"Extracted {len(constraints)} constraints from the user request:\n\n"
                f"{constraints_json}"
            )
            
        except Exception as e:
            return f"Error extracting constraints: {str(e)}"
    
    def _extract_constraints(self, user_request: str) -> List[Constraint]:
        """
        Extract constraints from the user request using pattern matching.
        In a real implementation, this would use LLM capabilities or more sophisticated NLP.
        
        Args:
            user_request: The user's travel request
            
        Returns:
            List of Constraint objects
        """
        constraints = []
        
        # Budget constraints
        budget_matches = re.findall(r'budget.*?(\$?[0-9,.]+)', user_request, re.IGNORECASE)
        for match in budget_matches:
            value = match.replace('$', '').replace(',', '')
            constraints.append(Constraint(
                type=ConstraintType.BUDGET,
                description=f"Keep total trip cost under ${value}",
                value=float(value),
                is_hard_constraint=True,
                layer="area"
            ))
        
        # Time constraints - dates
        date_matches = re.findall(r'(from|between|during)\s+([A-Za-z]+\s+\d{1,2}(?:st|nd|rd|th)?(?:,?\s+\d{4})?)\s+(?:to|and|until|through)\s+([A-Za-z]+\s+\d{1,2}(?:st|nd|rd|th)?(?:,?\s+\d{4})?)', user_request, re.IGNORECASE)
        for match in date_matches:
            constraints.append(Constraint(
                type=ConstraintType.TIME,
                description=f"Travel dates from {match[1]} to {match[2]}",
                value=f"{match[1]}-{match[2]}",
                is_hard_constraint=True,
                layer="area"
            ))
        
        # Time constraints - duration
        duration_matches = re.findall(r'(?:for|about|around)\s+(\d+)\s+(?:days|weeks)', user_request, re.IGNORECASE)
        for match in duration_matches:
            unit = "days" if "day" in user_request else "weeks"
            constraints.append(Constraint(
                type=ConstraintType.TIME,
                description=f"Trip duration of {match} {unit}",
                value=int(match),
                is_hard_constraint=True,
                layer="area"
            ))
        
        # Preference constraints - accommodation
        if re.search(r'(hotel|resort|luxury|accommodation|stay)', user_request, re.IGNORECASE):
            if re.search(r'luxury|5.star|five.star|high.end', user_request, re.IGNORECASE):
                constraints.append(Constraint(
                    type=ConstraintType.PREFERENCE,
                    description="Luxury or high-end accommodations preferred",
                    is_hard_constraint=False,
                    layer="within_city"
                ))
            elif re.search(r'budget|affordable|cheap|inexpensive', user_request, re.IGNORECASE):
                constraints.append(Constraint(
                    type=ConstraintType.PREFERENCE,
                    description="Budget-friendly accommodations preferred",
                    is_hard_constraint=False,
                    layer="within_city"
                ))
        
        # Preference constraints - activities
        if re.search(r'(hiking|outdoors|nature|adventure)', user_request, re.IGNORECASE):
            constraints.append(Constraint(
                type=ConstraintType.PREFERENCE,
                description="Include outdoor/adventure activities",
                is_hard_constraint=False,
                layer="within_city"
            ))
        
        if re.search(r'(museum|culture|history|art)', user_request, re.IGNORECASE):
            constraints.append(Constraint(
                type=ConstraintType.PREFERENCE,
                description="Include cultural/historical activities",
                is_hard_constraint=False,
                layer="within_city"
            ))
        
        if re.search(r'(food|cuisine|dining|restaurant)', user_request, re.IGNORECASE):
            constraints.append(Constraint(
                type=ConstraintType.PREFERENCE,
                description="Include culinary experiences",
                is_hard_constraint=False,
                layer="within_city"
            ))
        
        # Logistics constraints
        if re.search(r'(flight|fly)', user_request, re.IGNORECASE):
            constraints.append(Constraint(
                type=ConstraintType.LOGISTICS,
                description="Include flight transportation",
                is_hard_constraint=True,
                layer="city"
            ))
        
        if re.search(r'(car|drive|road.?trip)', user_request, re.IGNORECASE):
            constraints.append(Constraint(
                type=ConstraintType.LOGISTICS,
                description="Include car transportation",
                is_hard_constraint=True,
                layer="city"
            ))
        
        # Accessibility constraints
        if re.search(r'(wheelchair|accessible|disability)', user_request, re.IGNORECASE):
            constraints.append(Constraint(
                type=ConstraintType.ACCESSIBILITY,
                description="Ensure all accommodations and activities are wheelchair accessible",
                is_hard_constraint=True,
                layer="verification"
            ))
        
        # Safety constraints
        if re.search(r'(safe|security|family.friendly)', user_request, re.IGNORECASE):
            constraints.append(Constraint(
                type=ConstraintType.SAFETY,
                description="Ensure all areas are safe and family-friendly",
                is_hard_constraint=True,
                layer="verification"
            ))
        
        # If no constraints were found, add a default time constraint
        if not constraints:
            constraints.append(Constraint(
                type=ConstraintType.TIME,
                description="Default trip duration of 7 days",
                value=7,
                is_hard_constraint=False,
                layer="area"
            ))
        
        return constraints