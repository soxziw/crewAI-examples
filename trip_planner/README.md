# MAIA - Multi-Agent Itinerary Assistant with CrewAI

Welcome to MAIA (Multi-Agent Itinerary Assistant), an advanced constraint-aware travel planning system powered by [crewAI](https://crewai.com). This project leverages a hierarchical multi-agent system to create comprehensive travel plans tailored to your preferences while strictly adhering to your constraints.

## Overview

MAIA utilizes a team of specialized AI agents organized in a hierarchical structure to research destinations, find optimal travel options, search for accommodations, plan detailed itineraries, and ensure all user constraints are rigorously verified. The system is designed to provide a seamless and personalized travel planning experience that respects your requirements at every planning stage.

## Key Features

- **Hierarchical Multi-Agent Architecture**: Specialized agents at different planning layers (Area, City, Within-City, Verification)
- **Constraint-Aware Planning**: Strict enforcement of user constraints at each planning layer
- **Real-Time API Integration**: Connections to travel APIs for up-to-date information
- **Comprehensive Verification**: Built-in verification system to ensure constraints are met
- **Detailed Travel Reports**: Complete travel itineraries with all necessary details

## Hierarchical Planning Layers

MAIA employs a four-layer planning approach:

1. **Area Layer**: High-level destination selection and timeframe planning
2. **City Layer**: City selection, duration planning, and inter-city transit
3. **Within-City Layer**: Activities, accommodations, dining, and local transit
4. **Verification Layer**: Constraint verification across all planning aspects

## Installation

Ensure you have Python >=3.10 <3.13 installed. This project uses [UV](https://docs.astral.sh/uv/) for dependency management.

1. Install UV:

   ```bash
   pip install uv
   ```

2. Install dependencies:

   ```bash
   crewai install
   ```

3. Add your env variables to the `.env` file.

* `OPENAI_API_KEY` - API key for the [OpenAI API](https://platform.openai.com/docs/guides)
* `SERPAPI_API_KEY` - API key for the [Serp API](https://serpapi.com/dashboard)
* `SERPER_API_KEY` - API key for the [Serper](https://serper.dev/)

## Configuration

- `src/trip_planner/config/maia_agents.yaml`: Define AI agents for the hierarchical layers
- `src/trip_planner/config/maia_tasks.yaml`: Specify tasks for each agent in the hierarchy
- `src/trip_planner/maia_orchestrator.py`: Orchestrator that manages the planning process
- `src/trip_planner/main.py`: Entry point with support for both legacy and MAIA planning

## Usage

Run MAIA from the project root:

```bash
crewai run
```

This command initializes the hierarchical AI agents and executes the constraint-aware travel planning process based on your configurations.

## AI Agents by Layer

### Area Layer
- **Destination Region Specialist**: Selects optimal destination regions and timeframes

### City Layer
- **City Selection & Duration Specialist**: Selects cities and plans duration for each
- **Intercity Transit Specialist**: Plans optimal transit between cities

### Within-City Layer
- **Activities & Sites Specialist**: Plans daily activities and sightseeing
- **Accommodation Specialist**: Finds optimal accommodations in each city
- **Dining Specialist**: Recommends dining options for each day
- **Local Transit Specialist**: Plans local transportation within each city

### Verification Layer
- **Constraint Verification Specialist**: Ensures all constraints are satisfied
- **Itinerary Compiler**: Creates the final comprehensive travel plan

## Output

The system generates:

1. `maia_trip_plan.json`: Detailed JSON representation of the full travel plan
2. `maia_trip_report.md`: Human-readable travel report including:
   - Executive Summary
   - Trip Overview
   - Destination Information
   - Travel Options
   - Accommodation Details
   - Daily Itinerary
   - Dining Recommendations
   - Cost Estimates
   - Constraint Compliance Report

## How Constraints Are Enforced

MAIA extracts constraints from natural language requests and enforces them through:

1. **Constraint Parsing**: Extracting explicit and implicit constraints
2. **Layer Assignment**: Allocating constraints to appropriate planning layers
3. **Layer Verification**: Verifying constraints at each planning stage
4. **Final Verification**: Comprehensive verification across the entire plan
5. **Constraint Conflict Resolution**: Handling cases where constraints conflict

## Support

For assistance or inquiries:

- [Documentation](https://docs.crewai.com)
- [GitHub Repository](https://github.com/joaomdmoura/crewai)
- [Discord Community](https://discord.com/invite/X4JWnZnxPb)
- [Chat with our docs](https://chatg.pt/DWjSBZn)

Experience the future of constraint-aware travel planning with MAIA!