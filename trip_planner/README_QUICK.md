# Trip Planner - Quick Guide

## Overview

This project demonstrates MAIA (Multi-Agent Itinerary Assistant), a sophisticated travel planning system built using the CrewAI framework. It uses a hierarchical multi-agent architecture to create comprehensive travel plans that adhere to user constraints.

## What's Included

- **Example Output**: The `example_output` directory contains examples of what the system produces:
  - `maia_trip_report.md`: A detailed travel itinerary
  - `maia_trip_plan.json`: The complete travel plan in JSON format
  - `constraint_verification_report.md`: Analysis of constraint satisfaction

## Running the Example

Due to installation issues with the required dependencies, we've provided a script to show the example output:

```bash
python3 show_example.py
```

This will copy the example output files to your current directory for viewing.

## Key Features

1. **Hierarchical Planning**: Uses specialized agents at different layers:
   - Area Layer: High-level destination planning
   - City Layer: City selection and inter-city transit
   - Within-City Layer: Activities, accommodations, dining, and local transit
   - Verification Layer: Constraint verification

2. **Constraint Management**: Extracts constraints from natural language requests and enforces them through all planning stages

3. **Comprehensive Reports**: Generates detailed travel itineraries with all necessary information

## Project Structure

- `src/trip_planner/`: Main codebase
  - `maia_architecture.py`: Core architecture definitions
  - `maia_orchestrator.py`: Central planning orchestrator
  - `agents/`: Specialized agents by layer
  - `verification/`: Constraint verification system
  - `tools/`: Custom tools for planning
  - `config/`: Configuration files

## How It Works

1. The system parses natural language travel requests
2. It extracts constraints and preferences
3. It plans destinations, cities, and accommodations
4. It creates a detailed daily itinerary
5. It verifies all constraints are satisfied
6. It generates comprehensive reports

For full installation instructions, see the main README.md.