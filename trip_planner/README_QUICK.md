# Trip Planner - Quick Guide

## Overview

This project demonstrates MAIA (Multi-Agent Itinerary Assistant), a sophisticated travel planning system built using the CrewAI framework. It uses a hierarchical multi-agent architecture to create comprehensive travel plans that adhere to user constraints.

This enhanced version provides **interactive input capabilities** to plan trips using either natural language or structured inputs.

## What's Included

- **Interactive Trip Planning**: Dialog-based interface for collecting travel requirements
- **Two Planning Modes**:
  - **MAIA**: Advanced constraint-aware planning with natural language input
  - **Legacy**: Traditional structured input trip planner
- **Example Output**: The `example_output` directory shows what the system produces:
  - `maia_trip_report.md`: A detailed travel itinerary
  - `maia_trip_plan.json`: The complete travel plan in JSON format
  - `constraint_verification_report.md`: Analysis of constraint satisfaction

## Running the Interactive Planner

1. Make sure you have all dependencies installed:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the interactive trip planner:
   ```bash
   # Either use the run script
   ./run_planner.py
   
   # Or run the module directly
   python -m src.trip_planner.main
   ```

3. Follow the on-screen prompts to enter your trip details

## Command Line Arguments

- `--mode`: Choose between `maia` (default) or `legacy` planning modes
  ```bash
  ./run_planner.py --mode legacy
  ```

- `--output-dir`: Specify where to save output files (default: current directory)
  ```bash
  ./run_planner.py --output-dir ./my_trips
  ```

## Planning Modes

### MAIA Mode (Default)

MAIA uses natural language input to plan your trip. Simply describe your trip in everyday language, including:
- Where you want to go
- When and for how long
- Your preferences (activities, cuisine, etc.)
- Budget constraints
- Special requirements

Example:
```
I want to plan a 10-day trip to Japan in cherry blossom season.
I'd like to visit Tokyo and Kyoto, and enjoy traditional food and culture.
My budget is around $5000 excluding flights, and I'd prefer 3-4 star hotels.
I'll be traveling from San Francisco.
```

### Legacy Mode

The legacy mode uses a structured input format with individual prompts for:
- Destination location
- Travel timeline
- Origin location
- Preferences
- Constraints

## Personalization

The system reads user preferences from `knowledge/user_preference.txt` to personalize your planning experience:
- Your location (used as default origin)
- Your interests (incorporated into recommendations)

## Viewing Example Output

If you just want to see example outputs without running the planner:

```bash
python3 show_example.py
```

This will copy example output files to your current directory for viewing.

## Key Features

1. **Hierarchical Planning**: Uses specialized agents at different layers:
   - Area Layer: High-level destination planning
   - City Layer: City selection and inter-city transit
   - Within-City Layer: Activities, accommodations, dining, and local transit
   - Verification Layer: Constraint verification

2. **Constraint Management**: Extracts constraints from natural language requests and enforces them through all planning stages

3. **Comprehensive Reports**: Generates detailed travel itineraries with all necessary information

For more technical details, see the main README.md.