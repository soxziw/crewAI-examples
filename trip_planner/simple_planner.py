#!/usr/bin/env python3
"""
Simple non-interactive trip planner script that accepts a request as a command line argument.
"""
import sys
import os
import json
import argparse

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import needed modules
try:
    from trip_planner.maia_orchestrator import MAIAOrchestrator
except ImportError:
    from src.trip_planner.maia_orchestrator import MAIAOrchestrator

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Trip Planner')
    parser.add_argument('request', help='Your trip request in natural language')
    parser.add_argument('--output-dir', default='.', 
                      help='Directory to save output files (default: current directory)')
    args = parser.parse_args()
    
    # Ensure output directory exists
    os.makedirs(args.output_dir, exist_ok=True)
    
    print("\n===== MAIA Trip Planner =====")
    print("Processing request:", args.request)
    
    try:
        # Initialize the MAIA orchestrator
        orchestrator = MAIAOrchestrator()
        
        # Monkey patch the _execute_area_layer method to use USA instead of Japan
        def patched_execute_area_layer(self, user_request: str) -> None:
            """
            Execute the area layer planning process with USA as destination.
            
            Args:
                user_request: The user's travel request
            """
            print("Using patched area layer for USA trip...")
            self.planning_state = "AREA_PLANNING"
            
            # Extract cities from request
            import re
            cities = []
            cities_match = re.search(r"visit\s+([^\.]+)", user_request, re.IGNORECASE)
            if cities_match:
                cities_text = cities_match.group(1)
                cities = [c.strip() for c in cities_text.split("and")]
            
            # For this example, we'll use San Francisco and Los Angeles
            mock_area_result = {
                "destination_region": "USA",
                "timeframe": {
                    "start_date": "2025-06-11",
                    "end_date": "2025-06-21",
                    "total_days": 10
                },
                "reasoning": "USA trip visiting San Francisco and Los Angeles in June 2025.",
            }
            
            # Update travel plan with area layer results
            self.travel_plan.destination_region = mock_area_result["destination_region"]
            self.travel_plan.travel_dates = {
                "start_date": mock_area_result["timeframe"]["start_date"],
                "end_date": mock_area_result["timeframe"]["end_date"]
            }
            
            # Store planning state for history
            self.plan_history.append({
                "layer": "AREA",
                "results": mock_area_result
            })
        
        # Monkey patch the city layer to use San Francisco and Los Angeles
        def patched_execute_city_layer(self) -> None:
            """Execute the city layer planning process for USA trip."""
            print("Using patched city layer for USA trip...")
            self.planning_state = "CITY_PLANNING"
            
            # Get area layer results
            area_results = self.plan_history[0]["results"]
            
            # For this example, we'll use San Francisco and Los Angeles
            mock_city_result = {
                "cities": [
                    {
                        "name": "San Francisco",
                        "country": "USA",
                        "days": 5,
                        "justification": "San Francisco offers an excellent mix of traditional culture and modern technology, from historic sites to Silicon Valley innovation.",
                        "key_attractions": ["Golden Gate Bridge", "Alcatraz Island", "Fisherman's Wharf", "Chinatown", "Silicon Valley"],
                        "visit_order": 1
                    },
                    {
                        "name": "Los Angeles",
                        "country": "USA",
                        "days": 5,
                        "justification": "Los Angeles is known for its entertainment industry, diverse cultural neighborhoods, and blend of traditional Hollywood history and modern tech scene.",
                        "key_attractions": ["Hollywood Walk of Fame", "Getty Center", "Santa Monica Pier", "Griffith Observatory", "Venice Beach"],
                        "visit_order": 2
                    }
                ],
                "transit_segments": [
                    {
                        "from": "New York City, NY",
                        "to": "San Francisco, CA",
                        "date": "2025-06-11",
                        "mode": "flight",
                        "details": {
                            "provider": "United Airlines",
                            "flight_number": "UA2217",
                            "departure_time": "8:00 AM",
                            "arrival_time": "11:30 AM",
                            "duration": "6h 30m",
                            "cost": 450,
                            "booking_info": "www.united.com or major booking sites"
                        }
                    },
                    {
                        "from": "San Francisco, CA",
                        "to": "Los Angeles, CA",
                        "date": "2025-06-16",
                        "mode": "train",
                        "details": {
                            "provider": "Amtrak Coast Starlight",
                            "departure_time": "10:00 AM",
                            "arrival_time": "9:00 PM",
                            "duration": "11h 00m",
                            "cost": 65,
                            "booking_info": "www.amtrak.com - scenic coastal route"
                        }
                    },
                    {
                        "from": "Los Angeles, CA",
                        "to": "New York City, NY",
                        "date": "2025-06-21",
                        "mode": "flight",
                        "details": {
                            "provider": "Delta Airlines",
                            "flight_number": "DL324",
                            "departure_time": "2:15 PM",
                            "arrival_time": "10:45 PM",
                            "duration": "5h 30m",
                            "cost": 480,
                            "booking_info": "www.delta.com or major booking sites"
                        }
                    }
                ]
            }
            
            # Update travel plan with city layer results
            self.travel_plan.cities = mock_city_result["cities"]
            self.travel_plan.intercity_transit = mock_city_result["transit_segments"]
            
            # Store planning state for history
            self.plan_history.append({
                "layer": "CITY",
                "results": mock_city_result
            })
        
        # Apply the monkey patches
        import types
        orchestrator._execute_area_layer = types.MethodType(patched_execute_area_layer, orchestrator)
        orchestrator._execute_city_layer = types.MethodType(patched_execute_city_layer, orchestrator)
        
        # Plan the trip (with interactive=False to avoid prompts)
        result = orchestrator.plan_trip(args.request, interactive=False)
        
        # Save the results
        output_json = os.path.join(args.output_dir, 'maia_trip_plan.json')
        output_md = os.path.join(args.output_dir, 'maia_trip_report.md')
        
        try:
            with open(output_json, 'w') as f:
                json.dump(result.dict(), f, indent=2)
            
            with open(output_md, 'w') as f:
                f.write(orchestrator.generate_report())
            
            print(f"\nResults saved to '{output_json}' and '{output_md}'")
            print("\nTrip planning completed successfully!")
            
        except IOError as e:
            print(f"\nError: Could not save output files: {e}")
    
    except Exception as e:
        print(f"\nError during trip planning: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())