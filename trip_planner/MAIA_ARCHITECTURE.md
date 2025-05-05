# MAIA: Multi-Agent Itinerary Assistant Architecture

## Overview

MAIA is a constraint-aware travel planning system that employs a hierarchical multi-agent architecture to create comprehensive travel itineraries. The system is designed to strictly enforce user constraints at each level of planning, ensuring that the final itinerary meets all requirements.

## Key Components

### 1. Constraint Management System

The core of MAIA is its constraint management system, which:

- Extracts constraints from natural language user requests
- Categorizes constraints by type (budget, time, preference, logistics, accessibility, safety)
- Assigns constraints to appropriate planning layers
- Verifies constraint adherence at each planning stage
- Provides detailed verification reports

### 2. Hierarchical Planning Layers

MAIA employs a four-layer planning approach:

#### Area Layer
- **Focus**: High-level destination selection and timeframe planning
- **Constraints**: Overall budget, available dates, seasonal preferences, region preferences
- **Outputs**: Destination region, travel dates, high-level reasoning

#### City Layer
- **Focus**: City selection, duration allocation, and inter-city transit planning
- **Constraints**: Transit preferences, city-specific requirements, duration limitations
- **Outputs**: Cities to visit, days per city, inter-city transportation

#### Within-City Layer
- **Focus**: Detailed planning of activities, accommodations, dining, and local transit
- **Constraints**: Activity preferences, accommodation requirements, dining preferences, accessibility needs
- **Outputs**: Daily activities, accommodation options, dining recommendations, local transportation

#### Verification Layer
- **Focus**: Comprehensive verification across all planning aspects
- **Constraints**: All constraints from previous layers plus cross-cutting concerns
- **Outputs**: Verification report, final itinerary, constraint compliance assessment

### 3. Data Structures

#### Constraint
```python
class Constraint:
    type: ConstraintType  # budget, time, preference, logistics, accessibility, safety
    description: str  # Natural language description
    value: Optional[Union[str, int, float]]  # Specific value if applicable
    is_hard_constraint: bool  # Whether constraint must be satisfied (vs. preference)
    layer: Optional[str]  # Which layer this constraint applies to
```

#### TravelPlan
```python
class TravelPlan:
    # Area layer information
    destination_region: str
    travel_dates: Dict[str, str]  # start_date, end_date
    
    # City layer information
    cities: List[Dict[str, Union[str, int]]]  # city_name, num_days, etc.
    intercity_transit: Optional[List[Dict[str, str]]]
    
    # Within-city layer information
    accommodations: Optional[Dict[str, List[Dict[str, str]]]]
    activities: Optional[Dict[str, List[Dict[str, str]]]]
    dining: Optional[Dict[str, List[Dict[str, str]]]]
    local_transit: Optional[Dict[str, List[Dict[str, str]]]]
    
    # Daily itinerary (final output)
    daily_itinerary: Optional[List[Dict[str, Union[str, List[Dict[str, str]]]]]]
    
    # Constraints and verification
    applied_constraints: List[Constraint]
    constraint_verification: Optional[Dict[str, bool]]
```

### 4. Agent Types

MAIA employs specialized agents for each aspect of planning:

- **Destination Selector**: Area-level destination planning
- **City Selector**: City selection and duration planning
- **Intercity Transit Planner**: Inter-city transportation planning
- **Activities Planner**: Within-city activities and attractions
- **Accommodation Finder**: Accommodation options in each city
- **Dining Recommender**: Dining options for each day
- **Local Transit Planner**: Within-city transportation
- **Constraint Verifier**: Verification of constraint adherence
- **Itinerary Compiler**: Final itinerary compilation

## Planning Process

1. **User Request Analysis**
   - Extract constraints from natural language request
   - Categorize constraints by type and planning layer

2. **Area Layer Planning**
   - Select destination region(s)
   - Determine optimal travel dates
   - Verify area-level constraints

3. **City Layer Planning**
   - Select specific cities to visit
   - Allocate duration for each city
   - Plan inter-city transportation
   - Verify city-level constraints

4. **Within-City Layer Planning**
   - Plan daily activities for each city
   - Find accommodation options
   - Recommend dining options
   - Plan local transportation
   - Verify within-city constraints

5. **Verification and Compilation**
   - Perform comprehensive constraint verification
   - Compile final day-by-day itinerary
   - Generate detailed travel report
   - Provide constraint compliance assessment

## Constraint Verification Process

Constraint verification occurs at multiple levels:

1. **Layer-Specific Verification**
   - Each planning layer verifies its own constraints
   - Constraints are checked as soon as relevant information is available

2. **Cross-Layer Verification**
   - Some constraints span multiple layers
   - The verification layer performs cross-cutting constraint checks

3. **Final Verification**
   - Comprehensive verification after all planning is complete
   - Generates a detailed verification report

4. **Constraint Violation Handling**
   - Violations are categorized by severity (critical vs. minor)
   - Critical violations trigger replanning
   - Multiple resolution strategies may be suggested

## Implementation Details

MAIA is implemented using CrewAI, with the following structure:

- **maia_architecture.py**: Core data structures and architectural components
- **maia_orchestrator.py**: Central orchestrator that manages the planning process
- **verification/**: Constraint management and verification system
- **agents/**: Specialized agents for each planning layer
- **tools/**: Custom tools for constraint parsing, verification, and API integration
- **config/**: Configuration files for agents and tasks

## Integration with External APIs

MAIA integrates with various travel APIs for real-time data:

- Flight search APIs for inter-city transit
- Accommodation APIs for hotel and rental options
- Points of interest APIs for activities
- Transportation APIs for local transit options

## Advantages Over Traditional Approaches

1. **Hierarchical Planning**: Breaking down complex planning into manageable layers
2. **Explicit Constraint Representation**: Clear representation of constraints throughout planning
3. **Verification at Multiple Levels**: Catching constraint violations early
4. **Specialized Agents**: Agents with domain expertise for each aspect of planning
5. **Comprehensive Documentation**: Detailed reports explaining planning decisions

## Future Enhancements

1. **Learning from User Feedback**: Improving planning based on user satisfaction
2. **Handling Constraint Conflicts**: More sophisticated conflict resolution strategies
3. **Dynamic Replanning**: Adapting plans based on real-time changes
4. **Personalization**: Learning user preferences over time
5. **Integration with More APIs**: Adding more real-time data sources