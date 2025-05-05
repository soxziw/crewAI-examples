"""
MAIA: Multi-Agent Itinerary Assistant Architecture

This module defines the hierarchical multi-agent architecture for the MAIA system,
a constraint-aware travel planning system using LLMs.

Architecture Layers:
1. Area Layer - High-level destination selection with broad constraints
2. City Layer - City selection & inter-city transit planning
3. Within-City Layer - Local activities, accommodations, dining, local transit
4. Verification Layer - Cross-layer constraint verification

Each layer has specialized agents that handle specific aspects of travel planning
while ensuring constraints are verified throughout the planning process.
"""

from enum import Enum
from typing import Dict, List, Optional, Union
from pydantic import BaseModel, Field


class ConstraintType(Enum):
    """Types of constraints that can be applied in the travel planning process."""
    BUDGET = "budget"
    TIME = "time"
    PREFERENCE = "preference"
    LOGISTICS = "logistics"
    ACCESSIBILITY = "accessibility"
    SAFETY = "safety"


class Constraint(BaseModel):
    """A representation of a user constraint for travel planning."""
    type: ConstraintType
    description: str
    value: Optional[Union[str, int, float]] = None
    is_hard_constraint: bool = True
    layer: Optional[str] = None  # Which layer this constraint applies to
    
    def to_natural_language(self) -> str:
        """Convert constraint to natural language for agent consumption."""
        prefix = "Must" if self.is_hard_constraint else "Prefer to"
        return f"{prefix}: {self.description}"


class TravelPlan(BaseModel):
    """Complete travel plan with information from all layers."""
    # Area layer information
    destination_region: str
    travel_dates: Dict[str, str]  # start_date, end_date
    
    # City layer information
    cities: List[Dict[str, Union[str, int]]]  # city_name, num_days, etc.
    intercity_transit: Optional[List[Dict[str, str]]] = None
    
    # Within-city layer information
    accommodations: Optional[Dict[str, List[Dict[str, str]]]] = None  # city -> list of accommodation options
    activities: Optional[Dict[str, List[Dict[str, str]]]] = None  # city -> list of activities
    dining: Optional[Dict[str, List[Dict[str, str]]]] = None  # city -> list of dining options
    local_transit: Optional[Dict[str, List[Dict[str, str]]]] = None  # city -> list of local transit options
    
    # Daily itinerary (final output)
    daily_itinerary: Optional[List[Dict[str, Union[str, List[Dict[str, str]]]]]] = None
    
    # Constraints that were considered
    applied_constraints: List[Constraint] = []
    
    # Verification results
    constraint_verification: Optional[Dict[str, bool]] = None


class AgentLayer(Enum):
    """Different layers in the MAIA architecture."""
    AREA = "area"
    CITY = "city"
    WITHIN_CITY = "within_city"
    VERIFICATION = "verification"


class AgentType(Enum):
    """Types of agents within the MAIA system."""
    # Area layer
    DESTINATION_SELECTOR = "destination_selector"
    
    # City layer
    CITY_SELECTOR = "city_selector"
    INTERCITY_TRANSIT = "intercity_transit"
    
    # Within-city layer
    ACTIVITIES = "activities"
    ACCOMMODATION = "accommodation"
    DINING = "dining"
    LOCAL_TRANSIT = "local_transit"
    
    # Verification layer
    CONSTRAINT_VERIFIER = "constraint_verifier"
    ITINERARY_COMPILER = "itinerary_compiler"


class PlanningState(Enum):
    """States of the planning process."""
    NOT_STARTED = "not_started"
    AREA_PLANNING = "area_planning"
    CITY_PLANNING = "city_planning"
    WITHIN_CITY_PLANNING = "within_city_planning"
    VERIFICATION = "verification"
    COMPLETED = "completed"
    FAILED = "failed"


class MAIAOrchestrator:
    """
    Orchestrator that manages the hierarchical planning process 
    across different agent layers.
    """
    
    def __init__(self):
        self.planning_state = PlanningState.NOT_STARTED
        self.travel_plan = None
        self.constraints = []
        
    def extract_constraints(self, user_request: str) -> List[Constraint]:
        """
        Extract constraints from a user's natural language request.
        In a full implementation, this would use LLM capabilities.
        """
        # This would be implemented with LLM to extract constraints from user request
        pass
    
    def assign_constraints_to_layers(self, constraints: List[Constraint]) -> Dict[str, List[Constraint]]:
        """
        Assign constraints to appropriate planning layers.
        """
        layer_constraints = {
            AgentLayer.AREA.value: [],
            AgentLayer.CITY.value: [],
            AgentLayer.WITHIN_CITY.value: [],
            AgentLayer.VERIFICATION.value: [],
        }
        
        for constraint in constraints:
            # Logic to determine which layer should handle each constraint
            # For now, assign to verification layer by default
            if not constraint.layer:
                layer_constraints[AgentLayer.VERIFICATION.value].append(constraint)
            else:
                layer_constraints[constraint.layer].append(constraint)
                
        return layer_constraints
    
    def plan_trip(self, user_request: str) -> TravelPlan:
        """
        Main entry point to plan a trip based on user request.
        Orchestrates the hierarchical planning process.
        """
        # Extract constraints from user request
        self.constraints = self.extract_constraints(user_request)
        
        # Initialize travel plan
        self.travel_plan = TravelPlan(
            destination_region="",
            travel_dates={},
            cities=[],
            applied_constraints=self.constraints
        )
        
        # Execute planning layers in sequence
        try:
            # Area layer planning
            self.planning_state = PlanningState.AREA_PLANNING
            # Execute area planning agents
            
            # City layer planning
            self.planning_state = PlanningState.CITY_PLANNING
            # Execute city planning agents
            
            # Within-city layer planning
            self.planning_state = PlanningState.WITHIN_CITY_PLANNING
            # Execute within-city planning agents
            
            # Final verification
            self.planning_state = PlanningState.VERIFICATION
            # Execute verification agents
            
            self.planning_state = PlanningState.COMPLETED
            return self.travel_plan
            
        except Exception as e:
            self.planning_state = PlanningState.FAILED
            raise Exception(f"Trip planning failed: {str(e)}")


# Placeholder for agent configuration
MAIA_AGENT_CONFIG = {
    # Area layer
    AgentType.DESTINATION_SELECTOR.value: {
        "layer": AgentLayer.AREA.value,
        "role": "Destination Region Specialist",
        "goal": "Select the optimal destination region and timeframe based on user constraints",
        "tools": ["SerperDevTool", "ScrapeWebsiteTool"]
    },
    
    # City layer
    AgentType.CITY_SELECTOR.value: {
        "layer": AgentLayer.CITY.value,
        "role": "City Selection & Duration Specialist",
        "goal": "Select specific cities to visit and determine optimal duration for each",
        "tools": ["SerperDevTool", "ScrapeWebsiteTool"]
    },
    
    AgentType.INTERCITY_TRANSIT.value: {
        "layer": AgentLayer.CITY.value,
        "role": "Intercity Transit Specialist",
        "goal": "Plan optimal transit between selected cities",
        "tools": ["SerperDevTool", "ScrapeWebsiteTool", "FlightSearchTool"]
    },
    
    # Within-city layer
    AgentType.ACTIVITIES.value: {
        "layer": AgentLayer.WITHIN_CITY.value,
        "role": "Activities & Sites Specialist",
        "goal": "Identify optimal activities and sites to visit in each city",
        "tools": ["SerperDevTool", "ScrapeWebsiteTool"]
    },
    
    AgentType.ACCOMMODATION.value: {
        "layer": AgentLayer.WITHIN_CITY.value,
        "role": "Accommodation Specialist",
        "goal": "Find optimal accommodations in each city",
        "tools": ["SerperDevTool", "ScrapeWebsiteTool", "AccommodationSearchTool"]
    },
    
    AgentType.DINING.value: {
        "layer": AgentLayer.WITHIN_CITY.value,
        "role": "Dining Specialist",
        "goal": "Recommend dining options in each city",
        "tools": ["SerperDevTool", "ScrapeWebsiteTool"]
    },
    
    AgentType.LOCAL_TRANSIT.value: {
        "layer": AgentLayer.WITHIN_CITY.value,
        "role": "Local Transit Specialist",
        "goal": "Plan local transportation within each city",
        "tools": ["SerperDevTool", "ScrapeWebsiteTool"]
    },
    
    # Verification layer
    AgentType.CONSTRAINT_VERIFIER.value: {
        "layer": AgentLayer.VERIFICATION.value,
        "role": "Constraint Verification Specialist",
        "goal": "Verify all user constraints are met by the travel plan",
        "tools": []
    },
    
    AgentType.ITINERARY_COMPILER.value: {
        "layer": AgentLayer.VERIFICATION.value,
        "role": "Itinerary Compiler",
        "goal": "Compile verified plans into a comprehensive travel itinerary",
        "tools": []
    }
}