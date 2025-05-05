"""
MAIA: Multi-Agent Itinerary Assistant Orchestrator

This module provides the main orchestrator for the MAIA system, 
coordinating the hierarchical planning process across all agent layers.
"""

import json
import logging
from typing import Dict, List, Any, Optional
import os

try:
    # When installed as a package
    from trip_planner.maia_architecture import (
        TravelPlan, 
        Constraint, 
        AgentLayer, 
        PlanningState,
        AgentType
    )
    from trip_planner.tools.constraint_parser_tool import ConstraintParserTool
    from trip_planner.verification.constraint_manager import ConstraintManager
    from trip_planner.agents.area_layer import AreaLayerAgents
    from trip_planner.agents.city_layer import CityLayerAgents
    from trip_planner.agents.within_city_layer import WithinCityLayerAgents
except ImportError:
    # When running directly from source
    from src.trip_planner.maia_architecture import (
        TravelPlan, 
        Constraint, 
        AgentLayer, 
        PlanningState,
        AgentType
    )
    from src.trip_planner.tools.constraint_parser_tool import ConstraintParserTool
    from src.trip_planner.verification.constraint_manager import ConstraintManager
    from src.trip_planner.agents.area_layer import AreaLayerAgents
    from src.trip_planner.agents.city_layer import CityLayerAgents
    from src.trip_planner.agents.within_city_layer import WithinCityLayerAgents

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("MAIA")


class MAIAOrchestrator:
    """
    Main orchestrator for the MAIA system, managing the hierarchical planning process
    across all agent layers and enforcing constraints.
    """
    
    def __init__(self):
        """Initialize the MAIA orchestrator."""
        self.constraint_manager = ConstraintManager()
        self.planning_state = PlanningState.NOT_STARTED
        self.travel_plan = None
        self.constraints = []
        self.agent_config = self._load_agent_config()
        self.parser_tool = ConstraintParserTool()
        self.plan_history = []
        
    def _load_agent_config(self) -> Dict[str, Any]:
        """
        Load agent configuration from file or use default.
        
        Returns:
            Agent configuration dictionary
        """
        try:
            # Try to load from file
            config_path = os.path.join(
                os.path.dirname(__file__), 
                "config", 
                "maia_agents.yaml"
            )
            if os.path.exists(config_path):
                import yaml
                with open(config_path, 'r') as f:
                    return yaml.safe_load(f)
            
            # Use default config from architecture
            from trip_planner.maia_architecture import MAIA_AGENT_CONFIG
            return MAIA_AGENT_CONFIG
            
        except Exception as e:
            logger.error(f"Error loading agent config: {e}")
            # Fallback to empty config
            return {}
    
    def extract_constraints(self, user_request: str) -> List[Constraint]:
        """
        Extract constraints from a user's natural language request.
        
        Args:
            user_request: The user's travel request
            
        Returns:
            List of extracted constraints
        """
        logger.info("Extracting constraints from user request")
        
        try:
            # Use the constraint parser tool to extract constraints
            result = self.parser_tool._run(user_request)
            
            # Parse the constraints from the result
            # Find the JSON part in the result
            import re
            json_match = re.search(r"```json\n(.*?)\n```", result, re.DOTALL)
            if json_match:
                constraints_json = json_match.group(1)
            else:
                # Try to find JSON without markdown markers
                start_idx = result.find('[{')
                end_idx = result.rfind('}]') + 2
                
                if start_idx >= 0 and end_idx > start_idx:
                    constraints_json = result[start_idx:end_idx]
                else:
                    logger.warning("Could not extract constraints JSON from result")
                    return []
            
            # Parse the JSON
            constraints_data = json.loads(constraints_json)
            
            # Convert to Constraint objects
            constraints = []
            for c_data in constraints_data:
                constraints.append(Constraint(**c_data))
                
            logger.info(f"Extracted {len(constraints)} constraints")
            return constraints
            
        except Exception as e:
            logger.error(f"Error extracting constraints: {e}")
            return []
    
    def plan_trip(self, user_request: str, interactive: bool = True) -> TravelPlan:
        """
        Plan a trip based on a user's natural language request.
        
        Args:
            user_request: The user's travel request
            interactive: Whether to show interactive progress updates
            
        Returns:
            The completed travel plan
        """
        logger.info("Starting trip planning process")
        
        if interactive:
            print("\nStarting trip planning process...")
            print("Step 1/5: Analyzing your request and extracting constraints")
        
        # Extract constraints from user request
        self.constraints = self.extract_constraints(user_request)
        
        # Add constraints to the constraint manager
        self.constraint_manager.add_constraints(self.constraints)
        
        # Initialize travel plan
        self.travel_plan = TravelPlan(
            destination_region="",
            travel_dates={},
            cities=[],
            applied_constraints=self.constraints
        )
        
        # Execute planning layers in sequence
        try:
            if interactive:
                print("\nStep 2/5: Planning your destination area and timeframe")
                
            # Area layer planning
            self._execute_area_layer(user_request)
            
            if interactive:
                print(f"  • Destination region: {self.travel_plan.destination_region}")
                print(f"  • Travel dates: {self.travel_plan.travel_dates.get('start_date', 'TBD')} to {self.travel_plan.travel_dates.get('end_date', 'TBD')}")
                print("\nStep 3/5: Planning cities to visit and transportation between them")
            
            # City layer planning
            self._execute_city_layer()
            
            if interactive:
                cities_str = ", ".join([city.get("name", "Unknown") for city in self.travel_plan.cities])
                print(f"  • Cities: {cities_str}")
                print(f"  • Number of intercity transits: {len(self.travel_plan.intercity_transit) if hasattr(self.travel_plan, 'intercity_transit') else 0}")
                print("\nStep 4/5: Planning detailed activities, accommodations, and dining")
            
            # Within-city layer planning
            self._execute_within_city_layer()
            
            if interactive:
                print(f"  • Activities planned for {len(self.travel_plan.activities) if hasattr(self.travel_plan, 'activities') else 0} cities")
                print(f"  • Accommodations booked in {len(self.travel_plan.accommodations) if hasattr(self.travel_plan, 'accommodations') else 0} cities")
                print("\nStep 5/5: Verifying all constraints and generating final itinerary")
            
            # Final verification
            self._execute_verification_layer()
            
            if interactive:
                total_violations = len(self.travel_plan.constraint_verification.get("violations", [])) if hasattr(self.travel_plan, 'constraint_verification') else 0
                if total_violations > 0:
                    print(f"  • Warning: Found {total_violations} constraint violations")
                else:
                    print("  • All constraints verified successfully")
                print("\nTrip planning completed successfully!")
            
            logger.info("Trip planning completed successfully")
            self.planning_state = PlanningState.COMPLETED
            return self.travel_plan
            
        except Exception as e:
            logger.error(f"Trip planning failed: {e}")
            self.planning_state = PlanningState.FAILED
            if interactive:
                print(f"\nError: Trip planning failed: {str(e)}")
            raise Exception(f"Trip planning failed: {str(e)}")
    
    def _execute_area_layer(self, user_request: str) -> None:
        """
        Execute the area layer planning process.
        
        Args:
            user_request: The user's travel request
        """
        logger.info("Executing area layer planning")
        self.planning_state = PlanningState.AREA_PLANNING
        
        # Get area layer constraints
        area_constraints = self.constraint_manager.get_constraints_for_layer(AgentLayer.AREA)
        
        # Initialize area layer agents
        area_agents = AreaLayerAgents(self.agent_config)
        
        # Create and run area layer crew
        area_crew = area_agents.create_area_crew(user_request, area_constraints)
        
        # In a full implementation, we would run the crew and process results
        # area_result = area_crew.kickoff()
        
        # For this example, we'll use mock data
        mock_area_result = {
            "destination_region": "Japan",
            "timeframe": {
                "start_date": "2026-03-25",
                "end_date": "2026-04-05",
                "total_days": 12
            },
            "reasoning": "Japan is ideal for cherry blossom viewing in late March to early April. The timeframe allows sufficient exploration of Tokyo, Kyoto, and potentially Osaka or Hiroshima.",
        }
        
        # Update travel plan with area layer results
        self.travel_plan.destination_region = mock_area_result["destination_region"]
        self.travel_plan.travel_dates = {
            "start_date": mock_area_result["timeframe"]["start_date"],
            "end_date": mock_area_result["timeframe"]["end_date"]
        }
        
        # Store planning state for history
        self.plan_history.append({
            "layer": AgentLayer.AREA.value,
            "results": mock_area_result
        })
        
        # Verify area layer constraints
        verification_result = self.constraint_manager.verify_layer(
            AgentLayer.AREA,
            self.travel_plan
        )
        
        if not verification_result.passed:
            logger.warning(f"Area layer verification failed: {verification_result}")
            # In a full implementation, we might replan here
    
    def _execute_city_layer(self) -> None:
        """Execute the city layer planning process."""
        logger.info("Executing city layer planning")
        self.planning_state = PlanningState.CITY_PLANNING
        
        # Get city layer constraints
        city_constraints = self.constraint_manager.get_constraints_for_layer(AgentLayer.CITY)
        
        # Initialize city layer agents
        city_agents = CityLayerAgents(self.agent_config)
        
        # Get area layer results
        area_results = self.plan_history[0]["results"]
        
        # Create and run city layer crew
        # In a full implementation, we would run the crew and process results
        # city_crew = city_agents.create_city_crew(
        #     area_results["destination_region"],
        #     area_results["timeframe"],
        #     "San Francisco, CA",  # Origin location from user request
        #     city_constraints
        # )
        # city_result = city_crew.kickoff()
        
        # For this example, we'll use mock data
        mock_city_result = {
            "cities": [
                {
                    "name": "Tokyo",
                    "country": "Japan",
                    "days": 5,
                    "justification": "As Japan's vibrant capital, Tokyo offers a mix of traditional and ultra-modern attractions.",
                    "key_attractions": ["Shibuya Crossing", "Senso-ji Temple", "Tokyo Skytree", "Meiji Shrine", "Ueno Park for cherry blossoms"],
                    "visit_order": 1
                },
                {
                    "name": "Kyoto",
                    "country": "Japan",
                    "days": 4,
                    "justification": "Kyoto is Japan's cultural heart with numerous temples, traditional gardens, and geisha districts.",
                    "key_attractions": ["Fushimi Inari Shrine", "Kinkaku-ji (Golden Pavilion)", "Arashiyama Bamboo Grove", "Philosopher's Path for cherry blossoms"],
                    "visit_order": 2
                },
                {
                    "name": "Osaka",
                    "country": "Japan",
                    "days": 2,
                    "justification": "Nearby Kyoto, Osaka offers amazing food, a vibrant atmosphere, and serves as a good base for a day trip to Nara.",
                    "key_attractions": ["Osaka Castle", "Dotonbori district", "Kuromon Market", "Osaka Aquarium"],
                    "visit_order": 3
                }
            ],
            "transit_segments": [
                {
                    "from": "San Francisco, CA",
                    "to": "Tokyo, Japan",
                    "date": "2026-03-25",
                    "mode": "flight",
                    "details": {
                        "provider": "ANA",
                        "flight_number": "NH7",
                        "departure_time": "11:05 AM",
                        "arrival_time": "3:25 PM (next day)",
                        "duration": "11h 20m",
                        "cost": 950,
                        "booking_info": "www.ana.co.jp or major booking sites"
                    }
                },
                {
                    "from": "Tokyo, Japan",
                    "to": "Kyoto, Japan",
                    "date": "2026-03-30",
                    "mode": "train",
                    "details": {
                        "provider": "JR Shinkansen",
                        "departure_time": "10:00 AM",
                        "arrival_time": "12:15 PM",
                        "duration": "2h 15m",
                        "cost": 135,
                        "booking_info": "Japan Rail Pass recommended for tourists"
                    }
                },
                {
                    "from": "Kyoto, Japan",
                    "to": "Osaka, Japan",
                    "date": "2026-04-03",
                    "mode": "train",
                    "details": {
                        "provider": "JR Special Rapid Service",
                        "departure_time": "9:30 AM",
                        "arrival_time": "10:00 AM",
                        "duration": "30m",
                        "cost": 15,
                        "booking_info": "Japan Rail Pass covers this journey"
                    }
                },
                {
                    "from": "Osaka, Japan",
                    "to": "San Francisco, CA",
                    "date": "2026-04-05",
                    "mode": "flight",
                    "details": {
                        "provider": "United Airlines",
                        "flight_number": "UA35",
                        "departure_time": "5:20 PM",
                        "arrival_time": "11:05 AM (same day)",
                        "duration": "9h 45m",
                        "cost": 980,
                        "booking_info": "www.united.com or major booking sites"
                    }
                }
            ]
        }
        
        # Update travel plan with city layer results
        self.travel_plan.cities = mock_city_result["cities"]
        self.travel_plan.intercity_transit = mock_city_result["transit_segments"]
        
        # Store planning state for history
        self.plan_history.append({
            "layer": AgentLayer.CITY.value,
            "results": mock_city_result
        })
        
        # Verify city layer constraints
        verification_result = self.constraint_manager.verify_layer(
            AgentLayer.CITY,
            self.travel_plan
        )
        
        if not verification_result.passed:
            logger.warning(f"City layer verification failed: {verification_result}")
            # In a full implementation, we might replan here
    
    def _execute_within_city_layer(self) -> None:
        """Execute the within-city layer planning process."""
        logger.info("Executing within-city layer planning")
        self.planning_state = PlanningState.WITHIN_CITY_PLANNING
        
        # Get within-city layer constraints
        within_city_constraints = self.constraint_manager.get_constraints_for_layer(AgentLayer.WITHIN_CITY)
        
        # Initialize within-city layer agents
        within_city_agents = WithinCityLayerAgents(self.agent_config)
        
        # Process each city
        city_plans = {}
        for city in self.travel_plan.cities:
            logger.info(f"Planning for city: {city['name']}")
            
            # Determine arrival and departure dates for this city
            # In a full implementation, these would be calculated based on the itinerary
            if city["visit_order"] == 1:
                arrival_date = self.travel_plan.travel_dates["start_date"]
            else:
                # Find previous city's departure date
                prev_city = next(c for c in self.travel_plan.cities if c["visit_order"] == city["visit_order"] - 1)
                arrival_date = f"2026-{'03' if city['visit_order'] <= 2 else '04'}-{25 + sum(c['days'] for c in self.travel_plan.cities if c['visit_order'] < city['visit_order'])}"
            
            departure_date = f"2026-{'03' if city['visit_order'] < 2 else '04'}-{25 + sum(c['days'] for c in self.travel_plan.cities if c['visit_order'] <= city['visit_order'])}"
            
            # Create and run within-city crew for this city
            # In a full implementation, we would run the crew and process results
            # city_crew = within_city_agents.create_within_city_crew(
            #     city,
            #     arrival_date,
            #     departure_date,
            #     within_city_constraints
            # )
            # city_result = city_crew.kickoff()
            
            # For this example, we'll use mock data
            mock_city_result = {
                "activities": self._generate_mock_activities(city, arrival_date, city["days"]),
                "accommodations": self._generate_mock_accommodations(city, arrival_date, departure_date),
                "dining": self._generate_mock_dining(city, arrival_date, city["days"]),
                "local_transit": self._generate_mock_local_transit(city)
            }
            
            # Store city plan
            city_plans[city["name"]] = mock_city_result
        
        # Update travel plan with within-city layer results
        self.travel_plan.accommodations = {
            city: plans["accommodations"]["accommodations"] 
            for city, plans in city_plans.items()
        }
        
        self.travel_plan.activities = {
            city: plans["activities"]["days"] 
            for city, plans in city_plans.items()
        }
        
        self.travel_plan.dining = {
            city: plans["dining"]["daily_recommendations"] 
            for city, plans in city_plans.items()
        }
        
        self.travel_plan.local_transit = {
            city: plans["local_transit"]["daily_transit_plans"] 
            for city, plans in city_plans.items()
        }
        
        # Store planning state for history
        self.plan_history.append({
            "layer": AgentLayer.WITHIN_CITY.value,
            "results": city_plans
        })
        
        # Verify within-city layer constraints
        verification_result = self.constraint_manager.verify_layer(
            AgentLayer.WITHIN_CITY,
            self.travel_plan
        )
        
        if not verification_result.passed:
            logger.warning(f"Within-city layer verification failed: {verification_result}")
            # In a full implementation, we might replan here
    
    def _execute_verification_layer(self) -> None:
        """Execute the final verification layer process."""
        logger.info("Executing verification layer")
        self.planning_state = PlanningState.VERIFICATION
        
        # Get verification layer constraints (all constraints)
        verification_constraints = self.constraints
        
        # Generate a comprehensive daily itinerary
        self.travel_plan.daily_itinerary = self._generate_daily_itinerary()
        
        # Verify all constraints against the complete plan
        verification_result = self.constraint_manager.verify_layer(
            AgentLayer.VERIFICATION,
            self.travel_plan
        )
        
        # Store verification results
        self.travel_plan.constraint_verification = {
            "passed": verification_result.passed,
            "violations": [v.to_dict() for v in verification_result.violations]
        }
        
        # Store planning state for history
        self.plan_history.append({
            "layer": AgentLayer.VERIFICATION.value,
            "results": {
                "verification_passed": verification_result.passed,
                "violations_count": len(verification_result.violations)
            }
        })
        
        if not verification_result.passed:
            logger.warning(f"Final verification failed: {verification_result}")
            # In a full implementation, we might replan here
    
    def _generate_daily_itinerary(self) -> List[Dict[str, Any]]:
        """
        Generate a comprehensive daily itinerary from all planning layers.
        
        Returns:
            List of daily itinerary entries
        """
        itinerary = []
        
        # Calculate start date
        start_date = self.travel_plan.travel_dates["start_date"]
        year, month, day = map(int, start_date.split("-"))
        
        # For each city in visit order
        current_day = 1
        for city in sorted(self.travel_plan.cities, key=lambda x: x["visit_order"]):
            city_name = city["name"]
            
            # Get city activities, accommodations, dining, and transit info
            activities = self.travel_plan.activities.get(city_name, [])
            accommodations = self.travel_plan.accommodations.get(city_name, [])
            dining = self.travel_plan.dining.get(city_name, [])
            transit = self.travel_plan.local_transit.get(city_name, [])
            
            # For each day in this city
            for day_index in range(city["days"]):
                day_date = f"2026-{'03' if current_day <= 7 else '04'}-{(25 + current_day - 1) % 31}"
                
                # Create daily itinerary entry
                day_entry = {
                    "day": current_day,
                    "date": day_date,
                    "city": city_name,
                    "accommodation": accommodations[0] if accommodations else {},
                    "activities": [],
                    "meals": [],
                    "local_transit": []
                }
                
                # Add activities for this day
                for activity_entry in activities:
                    if activity_entry["day"] == day_index + 1:
                        day_entry["activities"].extend(activity_entry.get("activities", []))
                
                # Add meals for this day
                for dining_entry in dining:
                    if dining_entry["day"] == day_index + 1:
                        day_entry["meals"].extend(dining_entry.get("meals", []))
                
                # Add local transit for this day
                for transit_entry in transit:
                    if transit_entry["day"] == day_index + 1:
                        day_entry["local_transit"].extend(transit_entry.get("journeys", []))
                
                # Add special markers for arrival/departure days
                if day_index == 0 and city["visit_order"] > 1:
                    # Arrival day from previous city
                    prev_city = next(c for c in self.travel_plan.cities if c["visit_order"] == city["visit_order"] - 1)
                    day_entry["special_event"] = f"Transit from {prev_city['name']} to {city_name}"
                
                if day_index == city["days"] - 1 and city["visit_order"] < len(self.travel_plan.cities):
                    # Departure day to next city
                    next_city = next(c for c in self.travel_plan.cities if c["visit_order"] == city["visit_order"] + 1)
                    day_entry["special_event"] = f"Transit to {next_city['name']}"
                
                # Add to itinerary
                itinerary.append(day_entry)
                current_day += 1
        
        return itinerary
    
    def generate_report(self) -> str:
        """
        Generate a human-readable markdown report of the travel plan.
        
        Returns:
            Markdown report
        """
        if not self.travel_plan:
            return "No travel plan has been generated yet."
        
        report = []
        
        # Title and summary
        report.append(f"# Travel Itinerary: {self.travel_plan.destination_region}")
        report.append("")
        
        # Trip overview
        report.append("## Trip Overview")
        report.append("")
        report.append(f"- **Destination:** {self.travel_plan.destination_region}")
        report.append(f"- **Dates:** {self.travel_plan.travel_dates['start_date']} to {self.travel_plan.travel_dates['end_date']}")
        report.append(f"- **Duration:** {sum(city['days'] for city in self.travel_plan.cities)} days")
        report.append(f"- **Cities:** {', '.join(city['name'] for city in self.travel_plan.cities)}")
        report.append("")
        
        # Constraints
        report.append("## Trip Constraints")
        report.append("")
        for constraint in self.constraints:
            status = "✅" if self.travel_plan.constraint_verification and not any(
                v['constraint']['description'] == constraint.description 
                for v in self.travel_plan.constraint_verification.get('violations', [])
            ) else "❌"
            report.append(f"- {status} {constraint.to_natural_language()}")
        report.append("")
        
        # City summary
        report.append("## Cities")
        report.append("")
        for city in sorted(self.travel_plan.cities, key=lambda x: x["visit_order"]):
            report.append(f"### {city['name']}, {city['country']}")
            report.append("")
            report.append(f"**Duration:** {city['days']} days")
            report.append("")
            report.append(f"**Key Attractions:**")
            for attraction in city.get("key_attractions", []):
                report.append(f"- {attraction}")
            report.append("")
            report.append(f"**Why Visit:** {city.get('justification', 'No justification provided.')}")
            report.append("")
        
        # Transportation
        report.append("## Transportation")
        report.append("")
        
        if self.travel_plan.intercity_transit:
            report.append("### Intercity Transit")
            report.append("")
            report.append("| From | To | Date | Mode | Details |")
            report.append("|------|----|----|------|---------|")
            for transit in self.travel_plan.intercity_transit:
                details = transit["details"]
                details_str = f"{details.get('provider', '')}, {details.get('departure_time', '')} - {details.get('arrival_time', '')}, ${details.get('cost', '')}"
                report.append(f"| {transit['from']} | {transit['to']} | {transit['date']} | {transit['mode'].title()} | {details_str} |")
            report.append("")
        
        # Accommodations
        report.append("## Accommodations")
        report.append("")
        for city_name, accommodations in self.travel_plan.accommodations.items():
            report.append(f"### {city_name}")
            report.append("")
            for accom in accommodations:
                report.append(f"**{accom['name']}** - ${accom['total_price']} total")
                report.append("")
                report.append(f"- **Location:** {accom['location']}")
                report.append(f"- **Rating:** {accom['rating']} / 5")
                report.append("")
                report.append("**Amenities:**")
                for amenity in accom.get("amenities", [])[:5]:  # Limit to 5 amenities
                    report.append(f"- {amenity}")
                report.append("")
        
        # Daily Itinerary
        report.append("## Daily Itinerary")
        report.append("")
        
        if self.travel_plan.daily_itinerary:
            for day in self.travel_plan.daily_itinerary:
                report.append(f"### Day {day['day']}: {day['date']} - {day['city']}")
                report.append("")
                
                if day.get("special_event"):
                    report.append(f"**Special Event:** {day['special_event']}")
                    report.append("")
                
                report.append("#### Activities")
                for activity in day.get("activities", [])[:5]:  # Limit to 5 activities per day
                    report.append(f"- **{activity['name']}** ({activity['estimated_duration']})")
                    report.append(f"  {activity.get('description', '')[:100]}...")  # Truncate long descriptions
                
                report.append("")
                report.append("#### Meals")
                for meal in day.get("meals", []):
                    report.append(f"- **{meal['meal_type'].title()}:** {meal['venue']} ({meal['cuisine']})")
                
                report.append("")
                
                if day.get("accommodation", {}).get("name"):
                    report.append(f"**Accommodation:** {day['accommodation']['name']}")
                    report.append("")
        
        # Estimated costs
        report.append("## Estimated Costs")
        report.append("")
        
        # Calculate mock costs
        transportation_cost = sum(t["details"].get("cost", 0) for t in self.travel_plan.intercity_transit)
        accommodation_cost = sum(
            accom[0].get("total_price", 0) 
            for accom in self.travel_plan.accommodations.values() 
            if accom
        )
        activities_cost = 1000  # Mock value
        food_cost = 800  # Mock value
        local_transit_cost = 300  # Mock value
        
        total_cost = transportation_cost + accommodation_cost + activities_cost + food_cost + local_transit_cost
        
        report.append(f"- **Transportation:** ${transportation_cost}")
        report.append(f"- **Accommodation:** ${accommodation_cost}")
        report.append(f"- **Activities:** ${activities_cost}")
        report.append(f"- **Food & Dining:** ${food_cost}")
        report.append(f"- **Local Transit:** ${local_transit_cost}")
        report.append("")
        report.append(f"**Total Estimated Cost:** ${total_cost}")
        report.append("")
        
        # Footer
        report.append("---")
        report.append("")
        report.append("*This itinerary was generated using MAIA (Multi-Agent Itinerary Assistant), a constraint-aware travel planning system.*")
        
        return "\n".join(report)
    
    # Mock data generation methods for demonstration purposes
    
    def _generate_mock_activities(self, city: Dict[str, Any], start_date: str, duration: int) -> Dict[str, Any]:
        """Generate mock activities for a city."""
        activities = {
            "city": f"{city['name']}, {city['country']}",
            "days": []
        }
        
        # Generate activities for each day
        for day in range(1, duration + 1):
            day_date = f"2026-{'03' if int(start_date.split('-')[2]) + day <= 31 else '04'}-{(int(start_date.split('-')[2]) + day - 1) % 31 or 31}"
            
            # Different activities based on the city
            if city["name"] == "Tokyo":
                day_activities = [
                    {
                        "name": ["Shibuya Crossing", "Senso-ji Temple", "Tokyo Skytree", "Meiji Shrine", "Ueno Park"][day % 5],
                        "type": "sightseeing",
                        "description": "One of Tokyo's most iconic attractions",
                        "location": "Central Tokyo",
                        "estimated_duration": "2 hours",
                        "opening_hours": "9:00 AM - 5:00 PM",
                        "estimated_cost": 15,
                        "booking_required": False
                    },
                    {
                        "name": ["Akihabara Electronics District", "Harajuku Shopping", "Tokyo National Museum", "Tsukiji Outer Market", "Tokyo Tower"][day % 5],
                        "type": "activity",
                        "description": "Popular Tokyo attraction",
                        "location": "Tokyo",
                        "estimated_duration": "3 hours",
                        "opening_hours": "10:00 AM - 6:00 PM",
                        "estimated_cost": 20,
                        "booking_required": False
                    }
                ]
            elif city["name"] == "Kyoto":
                day_activities = [
                    {
                        "name": ["Fushimi Inari Shrine", "Kinkaku-ji (Golden Pavilion)", "Arashiyama Bamboo Grove", "Philosopher's Path", "Kiyomizu-dera Temple"][day % 5],
                        "type": "sightseeing",
                        "description": "Historic site in Kyoto",
                        "location": "Kyoto",
                        "estimated_duration": "2.5 hours",
                        "opening_hours": "8:30 AM - 5:30 PM",
                        "estimated_cost": 10,
                        "booking_required": False
                    },
                    {
                        "name": ["Nishiki Market", "Gion District", "Kyoto Imperial Palace", "Ryoan-ji Temple", "Nijo Castle"][day % 5],
                        "type": "activity",
                        "description": "Cultural experience in Kyoto",
                        "location": "Kyoto",
                        "estimated_duration": "2 hours",
                        "opening_hours": "9:00 AM - 5:00 PM",
                        "estimated_cost": 12,
                        "booking_required": False
                    }
                ]
            else:  # Osaka
                day_activities = [
                    {
                        "name": ["Osaka Castle", "Dotonbori", "Kuromon Market", "Osaka Aquarium", "Universal Studios Japan"][day % 5],
                        "type": "sightseeing",
                        "description": "Popular attraction in Osaka",
                        "location": "Osaka",
                        "estimated_duration": "3 hours",
                        "opening_hours": "9:00 AM - 6:00 PM",
                        "estimated_cost": 30,
                        "booking_required": day == 5,  # USJ requires booking
                    },
                    {
                        "name": ["Shinsekai", "Umeda Sky Building", "Sumiyoshi Taisha", "Nara Day Trip", "Tempozan Harbor Village"][day % 5],
                        "type": "activity",
                        "description": "Interesting place to visit in Osaka",
                        "location": "Osaka",
                        "estimated_duration": "2 hours",
                        "opening_hours": "10:00 AM - 8:00 PM",
                        "estimated_cost": 15,
                        "booking_required": False
                    }
                ]
            
            activities["days"].append({
                "day": day,
                "date": day_date,
                "activities": day_activities,
                "alternative_activities": [
                    {
                        "name": f"Alternative activity {i} for {city['name']} day {day}",
                        "reason_to_consider": "In case of rain or primary activity is unavailable"
                    } for i in range(1, 3)
                ],
                "estimated_total_cost": sum(a["estimated_cost"] for a in day_activities)
            })
        
        activities["estimated_total_activities_cost"] = sum(day["estimated_total_cost"] for day in activities["days"])
        
        return activities
    
    def _generate_mock_accommodations(self, city: Dict[str, Any], arrival_date: str, departure_date: str) -> Dict[str, Any]:
        """Generate mock accommodations for a city."""
        nights = (self._date_to_days(departure_date) - self._date_to_days(arrival_date))
        
        accommodations = {
            "city": f"{city['name']}, {city['country']}",
            "stay_duration": {
                "check_in": arrival_date,
                "check_out": departure_date,
                "total_nights": nights
            },
            "accommodations": []
        }
        
        # Different options based on the city
        if city["name"] == "Tokyo":
            accommodations["accommodations"] = [
                {
                    "name": "Hotel Century Southern Tower",
                    "type": "hotel",
                    "location": "Shinjuku, Tokyo",
                    "proximity_to_activities": "Central location, close to Shinjuku Station",
                    "price_per_night": 150,
                    "total_price": 150 * nights,
                    "rating": 4.5,
                    "amenities": ["Free WiFi", "Air conditioning", "Restaurant", "Bar", "24-hour front desk"],
                    "pros": ["Excellent location", "Great views", "Modern rooms"],
                    "cons": ["Smaller rooms", "Busy area"],
                    "booking_info": "Book directly on hotel website or through major booking platforms",
                    "cancellation_policy": "Free cancellation up to 7 days before check-in"
                },
                {
                    "name": "Citadines Central Shinjuku Tokyo",
                    "type": "apart-hotel",
                    "location": "Shinjuku, Tokyo",
                    "proximity_to_activities": "Walking distance to Shinjuku Gyoen and shopping areas",
                    "price_per_night": 130,
                    "total_price": 130 * nights,
                    "rating": 4.3,
                    "amenities": ["Kitchenette", "Free WiFi", "Air conditioning", "Washing machine"],
                    "pros": ["More space", "Kitchen facilities", "Good value"],
                    "cons": ["Fewer hotel services", "Dated decor"],
                    "booking_info": "Available on major booking platforms",
                    "cancellation_policy": "Free cancellation up to 5 days before check-in"
                }
            ]
        elif city["name"] == "Kyoto":
            accommodations["accommodations"] = [
                {
                    "name": "Kyoto Granbell Hotel",
                    "type": "hotel",
                    "location": "Gion, Kyoto",
                    "proximity_to_activities": "In the heart of the historic Gion district",
                    "price_per_night": 140,
                    "total_price": 140 * nights,
                    "rating": 4.4,
                    "amenities": ["Free WiFi", "Public bath", "Restaurant", "Bar", "Bicycle rental"],
                    "pros": ["Historic location", "Modern Japanese design", "Near temples"],
                    "cons": ["Rooms can be small", "Popular area can be busy"],
                    "booking_info": "Book directly on hotel website or through major booking platforms",
                    "cancellation_policy": "Free cancellation up to 7 days before check-in"
                },
                {
                    "name": "Hotel Resol Kyoto Kawaramachi Sanjo",
                    "type": "hotel",
                    "location": "Downtown Kyoto",
                    "proximity_to_activities": "Central location near shopping and dining",
                    "price_per_night": 120,
                    "total_price": 120 * nights,
                    "rating": 4.2,
                    "amenities": ["Free WiFi", "Air conditioning", "Restaurant", "Laundry service"],
                    "pros": ["Great location", "Clean rooms", "Helpful staff"],
                    "cons": ["Standard rooms", "Can be noisy"],
                    "booking_info": "Available on major booking platforms",
                    "cancellation_policy": "Free cancellation up to 3 days before check-in"
                }
            ]
        else:  # Osaka
            accommodations["accommodations"] = [
                {
                    "name": "Hotel Nikko Osaka",
                    "type": "hotel",
                    "location": "Namba, Osaka",
                    "proximity_to_activities": "Connected to Shinsaibashi shopping district",
                    "price_per_night": 135,
                    "total_price": 135 * nights,
                    "rating": 4.3,
                    "amenities": ["Free WiFi", "Multiple restaurants", "Bar", "Fitness center"],
                    "pros": ["Prime location", "Quality service", "Good amenities"],
                    "cons": ["Business-oriented", "Extra charges for facilities"],
                    "booking_info": "Book directly on hotel website or through major booking platforms",
                    "cancellation_policy": "Free cancellation up to 7 days before check-in"
                },
                {
                    "name": "Fraser Residence Nankai Osaka",
                    "type": "serviced apartment",
                    "location": "Near Namba Station",
                    "proximity_to_activities": "Close to Dotonbori and transportation",
                    "price_per_night": 125,
                    "total_price": 125 * nights,
                    "rating": 4.4,
                    "amenities": ["Kitchen", "Free WiFi", "Washing machine", "Fitness center"],
                    "pros": ["Spacious rooms", "Full kitchen", "Homey feel"],
                    "cons": ["Fewer hotel services", "Farther from some attractions"],
                    "booking_info": "Available on major booking platforms",
                    "cancellation_policy": "Free cancellation up to 5 days before check-in"
                }
            ]
        
        return accommodations
    
    def _generate_mock_dining(self, city: Dict[str, Any], start_date: str, duration: int) -> Dict[str, Any]:
        """Generate mock dining options for a city."""
        dining = {
            "city": f"{city['name']}, {city['country']}",
            "local_specialties": [],
            "daily_recommendations": [],
            "dining_budget_estimate": {
                "daily": 0,
                "total": 0
            }
        }
        
        # Local specialties based on city
        if city["name"] == "Tokyo":
            dining["local_specialties"] = [
                {"dish": "Sushi", "description": "Fresh raw fish on seasoned rice"},
                {"dish": "Ramen", "description": "Noodle soup with various toppings"},
                {"dish": "Monjayaki", "description": "Tokyo-style savory pancake"}
            ]
        elif city["name"] == "Kyoto":
            dining["local_specialties"] = [
                {"dish": "Kaiseki", "description": "Traditional multi-course meal"},
                {"dish": "Yudofu", "description": "Simmered tofu, a Kyoto specialty"},
                {"dish": "Matcha desserts", "description": "Green tea flavored sweets"}
            ]
        else:  # Osaka
            dining["local_specialties"] = [
                {"dish": "Takoyaki", "description": "Octopus-filled batter balls"},
                {"dish": "Okonomiyaki", "description": "Savory pancake with various ingredients"},
                {"dish": "Kushikatsu", "description": "Deep-fried skewers of meat and vegetables"}
            ]
        
        # Daily dining recommendations
        daily_cost = 0
        for day in range(1, duration + 1):
            day_date = f"2026-{'03' if int(start_date.split('-')[2]) + day <= 31 else '04'}-{(int(start_date.split('-')[2]) + day - 1) % 31 or 31}"
            
            # Different meals based on the city
            if city["name"] == "Tokyo":
                meals = [
                    {
                        "meal_type": "breakfast",
                        "venue": ["Hotel breakfast", "Tsukiji Market food stalls", "Cafe de L'ambre", "Convenience store", "Bread & Espresso"][day % 5],
                        "cuisine": "Japanese/International",
                        "price_range": "$-$$",
                        "location": "Near accommodation",
                        "proximity_to_activities": "Convenient starting point",
                        "recommended_dishes": ["Traditional Japanese breakfast set", "Pastries and coffee"],
                        "reservation_required": False
                    },
                    {
                        "meal_type": "lunch",
                        "venue": ["Ichiran Ramen", "Tonkatsu Maisen", "Sushi Dai", "Tempura Tsunahachi", "Udon Maruka"][day % 5],
                        "cuisine": "Japanese",
                        "price_range": "$$",
                        "location": "Near morning activities",
                        "proximity_to_activities": "Convenient midday break",
                        "recommended_dishes": ["Tonkotsu ramen", "Signature tempura set"],
                        "reservation_required": False
                    },
                    {
                        "meal_type": "dinner",
                        "venue": ["Gonpachi Nishi-Azabu", "Uobei Sushi", "Kobe Beef Kaiseki 511", "Yakitori Alley", "Robot Restaurant"][day % 5],
                        "cuisine": "Japanese",
                        "price_range": "$$$",
                        "location": "Shinjuku/Shibuya area",
                        "proximity_to_activities": "Evening entertainment district",
                        "recommended_dishes": ["Kaiseki course", "Assorted yakitori", "Conveyor belt sushi"],
                        "reservation_required": True,
                        "reservation_info": "Reserve 1-2 weeks in advance through concierge"
                    }
                ]
            elif city["name"] == "Kyoto":
                meals = [
                    {
                        "meal_type": "breakfast",
                        "venue": ["Hotel breakfast", "% Arabica Coffee", "Lorimer Kyoto", "Kyoto Saryo", "Len Kyoto"][day % 5],
                        "cuisine": "Japanese/Cafe",
                        "price_range": "$-$$",
                        "location": "Near accommodation",
                        "proximity_to_activities": "Convenient starting point",
                        "recommended_dishes": ["Matcha latte and pastry", "Japanese breakfast set"],
                        "reservation_required": False
                    },
                    {
                        "meal_type": "lunch",
                        "venue": ["Omen", "Yoshikawa Tempura", "Kyoto Gogyo", "Musashi Sushi", "Nishiki Market food stalls"][day % 5],
                        "cuisine": "Japanese",
                        "price_range": "$$",
                        "location": "Near temples/attractions",
                        "proximity_to_activities": "Along sightseeing route",
                        "recommended_dishes": ["Udon noodles", "Tempura set", "Market snacks"],
                        "reservation_required": False
                    },
                    {
                        "meal_type": "dinner",
                        "venue": ["Gion Kyoto", "Pontocho Alley restaurants", "Kichi Kichi Omurice", "Kyoto Kitcho", "Omen Kodaiji"][day % 5],
                        "cuisine": "Traditional Kyoto cuisine",
                        "price_range": "$$$-$$$$",
                        "location": "Gion district",
                        "proximity_to_activities": "Historic dining district",
                        "recommended_dishes": ["Kaiseki course", "Yudofu hot pot", "Seasonal specialties"],
                        "reservation_required": True,
                        "reservation_info": "Reserve through hotel concierge 1-3 weeks in advance"
                    }
                ]
            else:  # Osaka
                meals = [
                    {
                        "meal_type": "breakfast",
                        "venue": ["Hotel breakfast", "Brooklyn Roasting Company", "Tosabori Chanot", "Len Osaka", "Fujiya 1935 Bread"][day % 5],
                        "cuisine": "Japanese/Cafe",
                        "price_range": "$-$$",
                        "location": "Near accommodation",
                        "proximity_to_activities": "Convenient starting point",
                        "recommended_dishes": ["Artisanal bread and coffee", "Japanese breakfast set"],
                        "reservation_required": False
                    },
                    {
                        "meal_type": "lunch",
                        "venue": ["Takoyaki stands in Dotonbori", "Mizuno Okonomiyaki", "Kuromon Market food stalls", "Endo Sushi", "Kinryu Ramen"][day % 5],
                        "cuisine": "Osaka street food",
                        "price_range": "$-$$",
                        "location": "Dotonbori/Namba area",
                        "proximity_to_activities": "Famous food district",
                        "recommended_dishes": ["Takoyaki", "Okonomiyaki", "Fresh sushi"],
                        "reservation_required": False
                    },
                    {
                        "meal_type": "dinner",
                        "venue": ["Kani Doraku", "Zuboraya", "Kushikatsu Daruma", "Matsusaka Beef Yakiniku M", "Hariju"][day % 5],
                        "cuisine": "Osaka specialties",
                        "price_range": "$$$",
                        "location": "Dotonbori/Namba area",
                        "proximity_to_activities": "Evening entertainment district",
                        "recommended_dishes": ["Crab feast", "Kushikatsu set", "Premium yakiniku beef"],
                        "reservation_required": True,
                        "reservation_info": "Reserve 1 week in advance through hotel"
                    }
                ]
            
            # Calculate daily cost (simplified)
            day_cost = 25 + 30 + 80  # Breakfast + Lunch + Dinner
            daily_cost += day_cost
            
            dining["daily_recommendations"].append({
                "day": day,
                "date": day_date,
                "meals": meals
            })
        
        dining["dining_budget_estimate"]["daily"] = daily_cost // duration
        dining["dining_budget_estimate"]["total"] = daily_cost
        
        return dining
    
    def _generate_mock_local_transit(self, city: Dict[str, Any]) -> Dict[str, Any]:
        """Generate mock local transit options for a city."""
        transit = {
            "city": f"{city['name']}, {city['country']}",
            "transportation_overview": {
                "main_transit_options": [],
                "recommended_transit_passes": [],
                "transit_tips": []
            },
            "daily_transit_plans": [],
            "estimated_total_transit_cost": 0
        }
        
        # Transit options based on city
        if city["name"] == "Tokyo":
            transit["transportation_overview"]["main_transit_options"] = [
                {
                    "mode": "Subway/Metro",
                    "description": "Extensive metro system connecting all major areas",
                    "pros": "Fast, reliable, covers most tourist areas",
                    "cons": "Can be crowded during rush hour"
                },
                {
                    "mode": "JR Trains",
                    "description": "Japan Railways network including the Yamanote Line",
                    "pros": "Covered by JR Pass, connects major stations",
                    "cons": "Separate from metro system, requires different ticket"
                },
                {
                    "mode": "Taxi",
                    "description": "Abundant but expensive",
                    "pros": "Convenient for late night or luggage",
                    "cons": "Expensive, traffic can be heavy"
                }
            ]
            transit["transportation_overview"]["recommended_transit_passes"] = [
                {
                    "name": "Tokyo Metro 72-Hour Ticket",
                    "coverage": "All Tokyo Metro and Toei Subway lines",
                    "price": 1500,
                    "worth_it": True,
                    "where_to_buy": "Tokyo Metro stations, tourist information centers"
                },
                {
                    "name": "PASMO/Suica IC Card",
                    "coverage": "All trains, metros, buses in Tokyo area",
                    "price": 1000,
                    "worth_it": True,
                    "where_to_buy": "Any station, 1000 yen deposit + charge amount"
                }
            ]
        elif city["name"] == "Kyoto":
            transit["transportation_overview"]["main_transit_options"] = [
                {
                    "mode": "Bus",
                    "description": "Extensive bus network covering most tourist sites",
                    "pros": "Reaches places with no subway access, flat fare system",
                    "cons": "Can be slow due to traffic, crowded during peak times"
                },
                {
                    "mode": "Subway",
                    "description": "Two subway lines serving limited areas",
                    "pros": "Fast and reliable",
                    "cons": "Limited coverage, doesn't reach many temples"
                },
                {
                    "mode": "Bicycle",
                    "description": "Popular way to explore the flatter parts of Kyoto",
                    "pros": "Flexible, enjoyable way to see the city",
                    "cons": "Weather dependent, some areas hilly"
                }
            ]
            transit["transportation_overview"]["recommended_transit_passes"] = [
                {
                    "name": "Kyoto Bus Pass (1-Day)",
                    "coverage": "Unlimited city bus rides in central Kyoto",
                    "price": 600,
                    "worth_it": True,
                    "where_to_buy": "Bus terminals, tourist information centers"
                },
                {
                    "name": "ICOCA IC Card",
                    "coverage": "All trains, buses in Kansai region",
                    "price": 1000,
                    "worth_it": True,
                    "where_to_buy": "Any JR station, 1000 yen deposit + charge amount"
                }
            ]
        else:  # Osaka
            transit["transportation_overview"]["main_transit_options"] = [
                {
                    "mode": "Subway",
                    "description": "8 subway lines covering most of central Osaka",
                    "pros": "Fast, comprehensive, easy to navigate",
                    "cons": "Different companies operate different lines"
                },
                {
                    "mode": "JR Trains",
                    "description": "JR Osaka Loop Line circles the city center",
                    "pros": "Covered by JR Pass, convenient for certain areas",
                    "cons": "Limited coverage of tourist spots"
                },
                {
                    "mode": "Walking",
                    "description": "Many attractions are within walking distance",
                    "pros": "Free, good way to experience the city",
                    "cons": "Weather dependent, can be tiring"
                }
            ]
            transit["transportation_overview"]["recommended_transit_passes"] = [
                {
                    "name": "Osaka Amazing Pass (1-Day)",
                    "coverage": "Unlimited subway, bus, and tramway + free entry to 35+ attractions",
                    "price": 2800,
                    "worth_it": True,
                    "where_to_buy": "Tourist information centers, major hotels"
                },
                {
                    "name": "ICOCA IC Card",
                    "coverage": "All trains, buses in Kansai region",
                    "price": 1000,
                    "worth_it": True,
                    "where_to_buy": "Any JR station, 1000 yen deposit + charge amount"
                }
            ]
        
        # Common transit tips
        transit["transportation_overview"]["transit_tips"] = [
            "Look up your route before traveling using Google Maps or Japan Transit Planner app",
            "Avoid rush hour (7:30-9:00 AM and 5:00-7:00 PM) when possible",
            "Keep transit pass/card ready before reaching the gates",
            "Stand on the left on escalators (right in Osaka)",
            "Buses require exact change or transit card"
        ]
        
        # Generate daily transit plans (simplified)
        daily_cost = 0
        for day in range(1, city["days"] + 1):
            day_cost = 1200  # Average daily transit cost
            daily_cost += day_cost
            
            transit["daily_transit_plans"].append({
                "day": day,
                "date": f"2026-04-{day % 30 + 1}",  # Simplified date
                "journeys": [
                    {
                        "from": "Accommodation",
                        "to": f"Morning activity {day}",
                        "recommended_mode": "Subway",
                        "route_details": "Take subway line to nearest station, 5 min walk",
                        "estimated_time": "25 minutes",
                        "estimated_cost": 220,
                        "alternative_options": ["Taxi (faster but ¥1500)", "Bus (slower but scenic)"]
                    },
                    {
                        "from": f"Morning activity {day}",
                        "to": f"Lunch venue {day}",
                        "recommended_mode": "Walking",
                        "route_details": "Short walk through interesting neighborhood",
                        "estimated_time": "15 minutes",
                        "estimated_cost": 0,
                        "alternative_options": ["Taxi (not recommended unless bad weather)"]
                    },
                    {
                        "from": f"Lunch venue {day}",
                        "to": f"Afternoon activity {day}",
                        "recommended_mode": "Subway",
                        "route_details": "Take subway line to destination station",
                        "estimated_time": "30 minutes",
                        "estimated_cost": 220,
                        "alternative_options": ["Bus (more scenic but slower)"]
                    },
                    {
                        "from": f"Afternoon activity {day}",
                        "to": f"Dinner venue {day}",
                        "recommended_mode": "Subway",
                        "route_details": "Take subway line to dining area",
                        "estimated_time": "20 minutes",
                        "estimated_cost": 220,
                        "alternative_options": ["Taxi (recommended if tired, ¥1200)"]
                    },
                    {
                        "from": f"Dinner venue {day}",
                        "to": "Accommodation",
                        "recommended_mode": "Subway",
                        "route_details": "Take subway line back to accommodation",
                        "estimated_time": "25 minutes",
                        "estimated_cost": 220,
                        "alternative_options": ["Taxi (recommended if late, ¥1500)"]
                    }
                ],
                "daily_transit_cost": day_cost
            })
        
        transit["estimated_total_transit_cost"] = daily_cost
        
        return transit
    
    def _date_to_days(self, date_str: str) -> int:
        """Convert date string to days since epoch for simple date math."""
        year, month, day = map(int, date_str.split('-'))
        return (year * 365) + (month * 30) + day