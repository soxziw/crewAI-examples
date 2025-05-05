"""
City Layer Agents for MAIA

These agents handle the city-level planning, focusing on:
1. City selection and duration for each city
2. Inter-city transit planning
3. City-level constraint processing
"""

from crewai import Agent, Task, Crew
from crewai_tools import SerperDevTool, ScrapeWebsiteTool
from typing import Dict, Any, List

from trip_planner.maia_architecture import AgentLayer, Constraint
from trip_planner.tools.flight_search_tool import FlightSearchTool


class CityLayerAgents:
    """
    City Layer agents that handle city selection and inter-city transit planning.
    """
    
    def __init__(self, agent_config: Dict[str, Any]):
        """
        Initialize the City Layer agents.
        
        Args:
            agent_config: Agent configuration
        """
        self.agent_config = agent_config
        self.base_tools = [SerperDevTool(), ScrapeWebsiteTool()]
        
    def city_selector_agent(self) -> Agent:
        """
        Create an agent that selects cities to visit and determines duration for each.
        
        Returns:
            City selection agent
        """
        return Agent(
            role="City Selection & Duration Specialist",
            goal="Select specific cities to visit and determine optimal duration for each city",
            backstory="""
            You are a travel expert who excels at creating multi-city itineraries. 
            You have in-depth knowledge of global cities and their attractions, 
            and you're skilled at determining the optimal amount of time to spend 
            in each location. You balance the desire to see multiple destinations 
            with the need to have enough time to truly experience each place.
            """,
            tools=self.base_tools,
            verbose=True
        )
    
    def intercity_transit_agent(self) -> Agent:
        """
        Create an agent that plans optimal transit between selected cities.
        
        Returns:
            Intercity transit agent
        """
        return Agent(
            role="Intercity Transit Specialist",
            goal="Plan optimal transit between selected cities",
            backstory="""
            You are a transportation and logistics expert who specializes in planning 
            efficient travel between cities. You have extensive knowledge of flight 
            routes, train connections, bus services, and driving options. You excel 
            at finding the most time-efficient and cost-effective ways to travel 
            between destinations while adhering to travelers' constraints and preferences.
            """,
            tools=self.base_tools + [FlightSearchTool()],
            verbose=True
        )
    
    def city_selection_task(
        self, 
        destination_region: str,
        timeframe: Dict[str, Any],
        constraints: List[Constraint]
    ) -> Task:
        """
        Create a task for city selection and duration planning.
        
        Args:
            destination_region: The selected destination region
            timeframe: The optimized travel timeframe
            constraints: List of applicable constraints
            
        Returns:
            City selection task
        """
        # Convert constraints to natural language for the agent
        constraints_text = "\n".join([
            f"- {c.to_natural_language()}" for c in constraints
        ])
        
        return Task(
            description=f"""
            Based on the destination region ({destination_region}) and timeframe, select 
            the optimal cities to visit and determine how many days to spend in each city.
            
            Timeframe:
            Start date: {timeframe['start_date']}
            End date: {timeframe['end_date']}
            Total days: {timeframe['total_days']}
            
            Constraints to consider:
            {constraints_text}
            
            Your selection should balance seeing multiple destinations with having enough 
            time to meaningfully experience each place. Consider factors such as:
            
            1. Key attractions and experiences in each city
            2. Travel time between cities
            3. Logical geographical progression
            4. Variety of experiences (e.g., urban exploration, natural attractions)
            5. Alignment with user constraints and preferences
            
            Your output should include:
            1. List of recommended cities with number of days for each
            2. Brief explanation of why each city was selected
            3. Suggested order of cities to visit
            4. Rationale for the recommended duration in each city
            
            Format your response as a JSON object with the following structure:
            {{
                "cities": [
                    {{
                        "name": "string",
                        "country": "string",
                        "days": number,
                        "justification": "string",
                        "key_attractions": [
                            "string"
                        ],
                        "visit_order": number
                    }}
                ],
                "total_cities": number,
                "total_days": number,
                "constraints_addressed": [
                    "string"
                ],
                "general_rationale": "string"
            }}
            """,
            agent=self.city_selector_agent(),
            expected_output="A comprehensive city selection plan with recommended duration for each city."
        )
    
    def intercity_transit_task(
        self, 
        cities: List[Dict[str, Any]],
        timeframe: Dict[str, Any],
        origin_location: str,
        constraints: List[Constraint]
    ) -> Task:
        """
        Create a task for planning transit between cities.
        
        Args:
            cities: List of selected cities with visit order
            timeframe: The optimized travel timeframe
            origin_location: User's origin location
            constraints: List of applicable constraints
            
        Returns:
            Intercity transit task
        """
        # Convert constraints to natural language for the agent
        constraints_text = "\n".join([
            f"- {c.to_natural_language()}" for c in constraints
        ])
        
        # Format cities for the agent
        cities_text = "\n".join([
            f"{city['visit_order']}. {city['name']}, {city['country']} ({city['days']} days)"
            for city in sorted(cities, key=lambda x: x['visit_order'])
        ])
        
        return Task(
            description=f"""
            Plan the optimal transit between the selected cities based on the recommended 
            visit order and timeframe. Start from {origin_location} and include return 
            transit to the origin location.
            
            Cities to visit (in order):
            {cities_text}
            
            Timeframe:
            Start date: {timeframe['start_date']}
            End date: {timeframe['end_date']}
            
            Constraints to consider:
            {constraints_text}
            
            For each transit segment, recommend the optimal transportation mode (flight, 
            train, bus, car) considering factors such as:
            
            1. Distance and travel time
            2. Cost
            3. Convenience and comfort
            4. Environmental impact (if relevant to constraints)
            5. Scenic value (if relevant)
            
            Your output should include:
            1. Detailed transit plan for each segment
            2. Estimated travel time and cost for each segment
            3. Specific recommendations (flight numbers, train routes, etc.)
            4. Alternatives if the primary recommendation isn't available
            
            Include the initial journey from {origin_location} to the first city and 
            the return journey from the last city to {origin_location}.
            
            Format your response as a JSON object with the following structure:
            {{
                "transit_segments": [
                    {{
                        "from": "string (location name)",
                        "to": "string (location name)",
                        "date": "YYYY-MM-DD",
                        "mode": "string (flight, train, bus, car)",
                        "details": {{
                            "provider": "string",
                            "flight_number": "string (if applicable)",
                            "departure_time": "string",
                            "arrival_time": "string",
                            "duration": "string",
                            "cost": number,
                            "booking_info": "string"
                        }},
                        "alternatives": [
                            {{
                                "mode": "string",
                                "details": "string",
                                "pros": "string",
                                "cons": "string"
                            }}
                        ]
                    }}
                ],
                "total_transit_cost": number,
                "total_transit_time": "string",
                "constraints_addressed": [
                    "string"
                ],
                "notes": "string"
            }}
            """,
            agent=self.intercity_transit_agent(),
            expected_output="A detailed intercity transit plan connecting all selected cities."
        )
    
    def create_city_crew(
        self, 
        destination_region: str,
        timeframe: Dict[str, Any],
        origin_location: str,
        constraints: List[Constraint]
    ) -> Crew:
        """
        Create a crew of city layer agents.
        
        Args:
            destination_region: The selected destination region
            timeframe: The optimized travel timeframe
            origin_location: User's origin location
            constraints: List of applicable constraints
            
        Returns:
            Crew of city layer agents
        """
        # Create the city selection task
        city_selection_task = self.city_selection_task(
            destination_region, 
            timeframe, 
            constraints
        )
        
        # Note: The intercity transit task would normally be created after 
        # the city selection task results are available, in a sequential process
        
        return Crew(
            agents=[
                self.city_selector_agent(),
                self.intercity_transit_agent()
            ],
            tasks=[city_selection_task],
            verbose=True
        )