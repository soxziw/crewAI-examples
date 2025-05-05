# MAIA: Project Summary

## Overview

This project has transformed the original CrewAI trip planner into MAIA (Multi-Agent Itinerary Assistant), a sophisticated constraint-aware travel planning system using a hierarchical multi-agent architecture. The enhanced system addresses the limitations of traditional travel planning tools by employing specialized agents at different planning layers and incorporating strict constraint verification at each stage.

## Key Enhancements

### 1. Hierarchical Multi-Agent Architecture

We implemented a four-layer planning architecture:
- **Area Layer**: High-level destination selection
- **City Layer**: City selection & inter-city transit
- **Within-City Layer**: Activities, accommodation, dining, local transit
- **Verification Layer**: Cross-layer constraint verification

This structure allows for more focused planning at each level while maintaining coherence across the entire trip plan.

### 2. Constraint Management System

We developed a comprehensive constraint management system that:
- Extracts constraints from natural language requests
- Categorizes constraints by type and planning layer
- Enforces constraints at each planning stage
- Verifies constraint adherence across layers
- Generates detailed verification reports

### 3. Specialized Agents

We created specialized agents for each aspect of travel planning:
- Destination Region Specialist
- City Selection & Duration Specialist
- Intercity Transit Specialist
- Activities & Sites Specialist
- Accommodation Specialist
- Dining Specialist
- Local Transit Specialist
- Constraint Verification Specialist
- Itinerary Compiler

Each agent focuses on its specific domain, leading to more detailed and accurate planning.

### 4. Comprehensive Data Structures

We designed robust data structures to represent:
- Travel constraints with type, severity, and layer assignment
- Complete travel plans with information from all planning layers
- Planning states to track progress through the system
- Verification results with detailed violation information

### 5. Real-Time API Integration

We improved API integrations for:
- Flight search
- Accommodation search
- Constraint parsing and verification
- Points of interest data

### 6. Enhanced Configuration System

We created detailed configuration files:
- `maia_agents.yaml`: Defines all agents in the hierarchical system
- `maia_tasks.yaml`: Specifies tasks for each planning layer

## Project Structure

```
trip_planner/
├── src/trip_planner/
│   ├── maia_architecture.py     # Core architecture definitions
│   ├── maia_orchestrator.py     # Central planning orchestrator
│   ├── agents/                  # Specialized agents by layer
│   │   ├── area_layer.py
│   │   ├── city_layer.py
│   │   └── within_city_layer.py
│   ├── verification/            # Constraint verification system
│   │   ├── constraint_manager.py
│   ├── tools/                   # Custom tools for planning
│   │   ├── constraint_parser_tool.py
│   │   ├── constraint_verification_tool.py
│   │   ├── flight_search_tool.py
│   │   └── accommodation_search_tool.py
│   ├── config/                  # Configuration files
│   │   ├── maia_agents.yaml
│   │   └── maia_tasks.yaml
│   ├── crew.py                  # CrewAI integration
│   └── main.py                  # Entry point
├── MAIA_ARCHITECTURE.md         # Detailed architecture documentation
└── README.md                    # Project overview
```

## Implementation Details

### Constraint Extraction and Verification

One of the key innovations is the constraint extraction and verification system:

1. Natural language requests are analyzed to extract explicit and implicit constraints
2. Constraints are categorized by type (budget, time, preference, logistics, accessibility, safety)
3. Constraints are assigned to appropriate planning layers
4. Each layer verifies its relevant constraints as soon as information is available
5. A final verification pass ensures all constraints are satisfied across the entire plan

### Hierarchical Planning Process

The planning process flows through the hierarchical layers:

1. **Area Layer**:
   - Extract constraints from user request
   - Select destination region
   - Determine optimal travel dates
   - Verify area-level constraints

2. **City Layer**:
   - Select specific cities to visit
   - Allocate duration for each city
   - Plan inter-city transportation
   - Verify city-level constraints

3. **Within-City Layer**:
   - Plan activities for each city
   - Find accommodation options
   - Recommend dining options
   - Plan local transportation
   - Verify within-city constraints

4. **Verification Layer**:
   - Perform comprehensive constraint verification
   - Compile final day-by-day itinerary
   - Generate detailed travel report

## Future Work

While this implementation provides a solid foundation for MAIA, several areas could be further developed:

1. **Enhanced Real API Integrations**: Currently, some APIs are simulated. Integrating with real travel APIs would provide more accurate and up-to-date information.

2. **Improved Constraint Conflict Resolution**: Adding more sophisticated strategies for resolving conflicts between constraints.

3. **User Feedback Loop**: Implementing a mechanism to learn from user feedback to improve future planning.

4. **Dynamic Replanning**: Adding capability to adapt plans based on real-time changes or unexpected events.

5. **Performance Optimization**: Optimizing the planning process for faster results, especially for complex trips.

## Conclusion

The MAIA project has successfully transformed a basic trip planner into a sophisticated constraint-aware travel planning system. By employing a hierarchical multi-agent architecture with specialized agents and comprehensive constraint verification, MAIA can generate detailed, personalized travel plans that strictly adhere to user constraints and preferences. This approach demonstrates how large language models can be used effectively in a multi-agent system to solve complex planning problems while maintaining strict adherence to constraints.