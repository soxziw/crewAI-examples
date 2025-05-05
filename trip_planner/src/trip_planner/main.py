#!/usr/bin/env python
import sys
import warnings
import json

from trip_planner.crew import TripPlanner
from trip_planner.maia_orchestrator import MAIAOrchestrator

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

# This main file is intended to be a way for you to run your
# crew locally, so refrain from adding unnecessary logic into this file.
# Replace with inputs you want to test with, it will automatically
# interpolate any tasks and agents information

def run():
    """
    Run the crew.
    """

    # Choose between legacy trip planner and MAIA
    use_maia = True  # Set to False to use legacy trip planner

    # Sample inputs for testing
    inputs_europe = {
        'destination_location': 'Krakow, Poland',
        'travel_timeline': '14 days in July 2025',
        'origin_location': 'San Jose, CA',
        'preferences': 'Historical sites, local cuisine, budget-friendly options',
        'constraints': 'Budget of $3000, no more than 2 hours of walking per day'
    }

    inputs_local = {
        'destination_location': 'Monterey, CA',
        'travel_timeline': 'weekend in May 2025',
        'origin_location': 'San Jose, CA',
        'preferences': 'Seafood, coastal views, relaxing activities',
        'constraints': 'Pet-friendly accommodations, avoid crowds'
    }
    
    inputs_maia_complex = {
        'request': """
        I want to plan a trip to explore the highlights of Japan for about 10 days in cherry blossom season (late March to early April 2026). 
        We'd like to visit Tokyo and Kyoto for sure, with possibly one or two other cities if it makes sense. 
        We prefer a mix of traditional cultural experiences and modern attractions, and enjoy good food (especially sushi and ramen).
        Our budget is around $5000 per person excluding flights, and we'd prefer clean, convenient hotels (3-4 star range). 
        We want to use public transportation as much as possible and are comfortable with walking up to 5 miles per day.
        We would fly from San Francisco and would need recommendations for both international flights and local transportation between cities.
        """
    }
    
    try:
        if use_maia:
            # Use the MAIA orchestrator for constraint-aware planning
            orchestrator = MAIAOrchestrator()
            result = orchestrator.plan_trip(inputs_maia_complex['request'])
            
            # Save the result to a file
            with open('maia_trip_plan.json', 'w') as f:
                json.dump(result.dict(), f, indent=2)
                
            # Also generate a readable markdown report
            with open('maia_trip_report.md', 'w') as f:
                f.write(orchestrator.generate_report())
                
            print("MAIA trip planning completed successfully!")
            print("Results saved to 'maia_trip_plan.json' and 'maia_trip_report.md'")
            
        else:
            # Use the legacy trip planner
            TripPlanner().crew().kickoff(inputs=inputs_local)
            
    except Exception as e:
        raise Exception(f"An error occurred while running the crew: {e}")


def train():
    """
    Train the crew for a given number of iterations.
    """
    inputs = {
        "topic": "AI LLMs"
    }
    try:
        TripPlanner().crew().train(n_iterations=int(sys.argv[1]), filename=sys.argv[2], inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while training the crew: {e}")

def replay():
    """
    Replay the crew execution from a specific task.
    """
    try:
        TripPlanner().crew().replay(task_id=sys.argv[1])

    except Exception as e:
        raise Exception(f"An error occurred while replaying the crew: {e}")

def test():
    """
    Test the crew execution and returns the results.
    """
    inputs = {
        "topic": "AI LLMs"
    }
    try:
        TripPlanner().crew().test(n_iterations=int(sys.argv[1]), openai_model_name=sys.argv[2], inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while testing the crew: {e}")