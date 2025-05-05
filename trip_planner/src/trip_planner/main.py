#!/usr/bin/env python
import sys
import warnings
import json
import os
import argparse

# Update imports to work with direct execution
try:
    # When installed as a package
    from trip_planner.crew import TripPlanner
    from trip_planner.maia_orchestrator import MAIAOrchestrator
except ModuleNotFoundError:
    # When running directly from source
    from src.trip_planner.crew import TripPlanner
    from src.trip_planner.maia_orchestrator import MAIAOrchestrator

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

def get_user_preferences():
    """
    Read user preferences from knowledge/user_preference.txt
    Returns a dictionary with user preferences
    """
    preferences = {}
    pref_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
        "knowledge",
        "user_preference.txt"
    )
    
    if os.path.exists(pref_path):
        try:
            with open(pref_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line.startswith('User name is'):
                        preferences['name'] = line.replace('User name is', '').strip().strip('.')
                    elif line.startswith('User is an'):
                        preferences['occupation'] = line.replace('User is an', '').strip().strip('.')
                    elif line.startswith('User is a'):
                        preferences['occupation'] = line.replace('User is a', '').strip().strip('.')
                    elif line.startswith('User is interested in'):
                        preferences['interests'] = line.replace('User is interested in', '').strip().strip('.')
                    elif line.startswith('User is based in'):
                        preferences['location'] = line.replace('User is based in', '').strip().strip('.')
        except Exception as e:
            print(f"Warning: Could not read user preferences: {e}")
    
    return preferences

def get_legacy_inputs():
    """
    Interactive input function for legacy trip planner
    Returns a dictionary with structured inputs
    """
    print("\n===== Trip Planner Input =====")
    print("Please provide the following information for your trip:")
    
    inputs = {}
    
    # Get user preferences
    user_prefs = get_user_preferences()
    default_origin = user_prefs.get('location', '')
    
    # Destination validation (requires at least a city or country)
    while True:
        inputs['destination_location'] = input(f"\nWhere would you like to go? (e.g., 'Paris, France'): ").strip()
        if not inputs['destination_location']:
            print("⚠️ Destination is required.")
            continue
        
        # Simple validation - check if it's at least 3 characters and doesn't contain numbers
        if len(inputs['destination_location']) < 3:
            print("⚠️ Please enter a valid destination (at least 3 characters).")
            continue
        
        if any(c.isdigit() for c in inputs['destination_location']):
            verify = input("⚠️ Your destination contains numbers. Is this correct? (y/n): ").strip().lower()
            if verify != 'y':
                continue
        
        break
    
    # Timeline validation (requires days/weeks/months and a year or season)
    while True:
        inputs['travel_timeline'] = input("\nWhen and how long will your trip be? (e.g., '7 days in August 2025'): ").strip()
        if not inputs['travel_timeline']:
            print("⚠️ Travel timeline is required.")
            continue
        
        # Simple validation - check for duration and timeframe
        has_duration = any(term in inputs['travel_timeline'].lower() for term in ['day', 'days', 'week', 'weeks', 'month', 'months'])
        has_timeframe = any(str(year) in inputs['travel_timeline'] for year in range(2024, 2031)) or any(
            season in inputs['travel_timeline'].lower() for season in 
            ['spring', 'summer', 'fall', 'autumn', 'winter', 'january', 'february', 'march', 'april', 'may', 'june', 
             'july', 'august', 'september', 'october', 'november', 'december'])
        
        if not has_duration:
            print("⚠️ Please include duration (e.g., '7 days', '2 weeks', '1 month').")
            continue
            
        if not has_timeframe:
            print("⚠️ Please include when you'll travel (e.g., 'August 2025', 'summer 2024').")
            continue
            
        break
    
    # Origin location with default from user preferences
    origin_prompt = f"\nWhere will you be traveling from? (e.g., 'New York, NY'"
    if default_origin:
        origin_prompt += f", press Enter for default: {default_origin}"
    origin_prompt += "): "
    
    while True:
        inputs['origin_location'] = input(origin_prompt).strip()
        if not inputs['origin_location'] and default_origin:
            inputs['origin_location'] = default_origin
            break
            
        if not inputs['origin_location']:
            print("⚠️ Origin location is required.")
            continue
            
        if len(inputs['origin_location']) < 3:
            print("⚠️ Please enter a valid origin location (at least 3 characters).")
            continue
            
        break
    
    # Preferences - optional but recommended
    while True:
        inputs['preferences'] = input("\nWhat are your travel preferences? (e.g., 'Historical sites, local cuisine'): ").strip()
        
        if not inputs['preferences']:
            verify = input("⚠️ No preferences entered. This helps personalize your trip. Continue anyway? (y/n): ").strip().lower()
            if verify == 'y':
                break
            continue
            
        if len(inputs['preferences']) < 5:
            print("⚠️ Please provide more detailed preferences for better results.")
            continue
            
        break
    
    # Constraints - optional
    inputs['constraints'] = input("\nAny constraints for your trip? (e.g., 'Budget of $3000, wheelchair accessible'): ").strip()
    
    # Confirm inputs
    print("\n===== Trip Details =====")
    print(f"Destination: {inputs['destination_location']}")
    print(f"Timeline: {inputs['travel_timeline']}")
    print(f"Origin: {inputs['origin_location']}")
    print(f"Preferences: {inputs['preferences'] or 'None specified'}")
    print(f"Constraints: {inputs['constraints'] or 'None specified'}")
    
    confirm = input("\nIs this information correct? (y/n): ").strip().lower()
    if confirm != 'y':
        print("Let's try again...")
        return get_legacy_inputs()
    
    print("\nThank you! Planning your trip...")
    return inputs

def get_maia_inputs():
    """
    Interactive input function for MAIA trip planner
    Returns a dictionary with natural language request
    """
    print("\n===== MAIA Trip Planner =====")
    print("Please describe your trip request in natural language.")
    print("Include details about:")
    print("- Destination(s) you want to visit")
    print("- Trip duration and timeframe")
    print("- Your travel preferences and interests")
    print("- Budget constraints")
    print("- Accommodation preferences")
    print("- Any special requirements\n")
    
    # Get user preferences
    user_prefs = get_user_preferences()
    default_origin = user_prefs.get('location', '')
    
    # Example prompt based on user preferences
    example = f"Example: I want to plan a 10-day trip to Italy in June 2025."
    if default_origin:
        example += f" I'll be flying from {default_origin}."
    if user_prefs.get('interests'):
        example += f" I'm particularly interested in {user_prefs.get('interests')}."
    print(f"{example}\n")
    
    # Get natural language request
    print("Enter your trip request (type on multiple lines, enter twice to finish):")
    lines = []
    while True:
        line = input()
        if not line and lines and not lines[-1]:  # Two consecutive empty lines
            break
        lines.append(line)
    
    request = "\n".join(lines).strip()
    
    # Validate request content
    while True:
        if not request:
            print("⚠️ Please enter a trip request:")
            request = input().strip()
            continue
            
        if len(request) < 20:
            print("⚠️ Your request is too short. Please provide more details for better results.")
            print("Enter your updated request:")
            request = input().strip()
            continue
        
        # Check for essential trip information
        missing_info = []
        
        if not any(word in request.lower() for word in ["to", "visit", "go to", "traveling to", "destination"]):
            missing_info.append("destination")
            
        if not any(word in request.lower() for word in ["days", "weeks", "month", "night", "duration", "length"]):
            missing_info.append("trip duration")
            
        if not any(str(year) in request for year in range(2024, 2031)) and not any(
            month in request.lower() for month in 
            ["january", "february", "march", "april", "may", "june", "july", "august", 
             "september", "october", "november", "december", "spring", "summer", "fall", "winter"]):
            missing_info.append("when you plan to travel")
        
        if default_origin and default_origin.lower() not in request.lower() and not any(
            word in request.lower() for word in ["from", "departure", "flying from", "leaving from"]):
            # Automatically add origin if it's missing but we have it from user preferences
            request += f" I'll be departing from {default_origin}."
            print(f"✅ Added departure location: {default_origin}")
        
        if missing_info:
            print(f"\n⚠️ Your request is missing some important information: {', '.join(missing_info)}")
            prompt = "Would you like to:\n1. Add the missing information\n2. Continue anyway\nEnter your choice (1/2): "
            choice = input(prompt).strip()
            
            if choice == "1":
                print("\nPlease enter your updated request with the missing information:")
                new_request = input().strip()
                if new_request:
                    request = new_request
                    continue
            else:
                print("Continuing with the current request...")
                break
        else:
            break
    
    # Confirm request
    print("\n===== Your Trip Request =====")
    print(request)
    confirm = input("\nIs this request correct? (y/n): ").strip().lower()
    
    if confirm != 'y':
        print("Let's update your request.")
        return get_maia_inputs()
    
    return {'request': request}

def run():
    """
    Run the crew with interactive user input.
    """
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Trip Planner')
    parser.add_argument('--mode', choices=['maia', 'legacy'], default='maia',
                       help='Planning mode: maia (default) or legacy')
    parser.add_argument('--output-dir', default='.',
                       help='Directory to save output files (default: current directory)')
    args = parser.parse_args()

    # Determine which planner to use
    use_maia = args.mode == 'maia'
    
    # Ensure output directory exists
    os.makedirs(args.output_dir, exist_ok=True)
    
    # Get interactive inputs based on planner type
    if use_maia:
        inputs = get_maia_inputs()
    else:
        inputs = get_legacy_inputs()
    
    try:
        if use_maia:
            # Use the MAIA orchestrator for constraint-aware planning
            orchestrator = MAIAOrchestrator()
            
            try:
                # Start the planning process
                result = orchestrator.plan_trip(inputs['request'], interactive=True)
                
                # Save the result to files
                output_json = os.path.join(args.output_dir, 'maia_trip_plan.json')
                output_md = os.path.join(args.output_dir, 'maia_trip_report.md')
                
                try:
                    with open(output_json, 'w') as f:
                        json.dump(result.dict(), f, indent=2)
                    
                    # Also generate a readable markdown report
                    with open(output_md, 'w') as f:
                        f.write(orchestrator.generate_report())
                    
                    print(f"\nResults saved to '{output_json}' and '{output_md}'")
                except IOError as save_error:
                    print(f"\n⚠️ Warning: Could not save output files: {save_error}")
                    print("Trip planning completed, but results could not be saved.")
                
            except KeyError as ke:
                print(f"\n❌ Error: Missing required information: {ke}")
                print("Please ensure your request includes all necessary details like destination, dates, etc.")
                return
                
            except ValueError as ve:
                print(f"\n❌ Error: Invalid value provided: {ve}")
                print("Please check your input and try again.")
                return
                
            except Exception as planning_error:
                print(f"\n❌ Error during trip planning: {planning_error}")
                
                # Give user option to retry with more information
                retry = input("\nWould you like to try again with a more detailed request? (y/n): ").strip().lower()
                if retry == 'y':
                    # Recursive call with new input
                    print("\nLet's try again with more details...")
                    inputs = get_maia_inputs()
                    run()
                return
            
        else:
            # Use the legacy trip planner
            try:
                print("\nUsing legacy trip planner...")
                TripPlanner().crew().kickoff(inputs=inputs)
                print("\nLegacy trip planning completed.")
            except Exception as legacy_error:
                print(f"\n❌ Error using legacy trip planner: {legacy_error}")
                
                # Give user option to retry
                retry = input("\nWould you like to try again? (y/n): ").strip().lower()
                if retry == 'y':
                    # Recursive call with new input
                    print("\nLet's try again...")
                    inputs = get_legacy_inputs()
                    run()
                return
            
    except Exception as e:
        print(f"\n❌ An unexpected error occurred: {e}")
        print("If this issue persists, please contact support.")


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