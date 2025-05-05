"""
Within-City Layer Agents for MAIA

These agents handle the detailed within-city planning, focusing on:
1. Activities and points of interest
2. Accommodation options
3. Dining recommendations
4. Local transportation
"""

from crewai import Agent, Task, Crew
# Instead of importing from crewai_tools, use our mock implementation
from typing import Dict, Any, List

# Import the mock tools from crew.py
try:
    from trip_planner.crew import SerperDevTool, ScrapeWebsiteTool
    from trip_planner.maia_architecture import AgentLayer, Constraint
    from trip_planner.tools.accommodation_search_tool import AccommodationSearchTool
except ImportError:
    from src.trip_planner.crew import SerperDevTool, ScrapeWebsiteTool
    from src.trip_planner.maia_architecture import AgentLayer, Constraint
    from src.trip_planner.tools.accommodation_search_tool import AccommodationSearchTool


class WithinCityLayerAgents:
    """
    Within-City Layer agents that handle detailed local planning.
    """
    
    def __init__(self, agent_config: Dict[str, Any]):
        """
        Initialize the Within-City Layer agents.
        
        Args:
            agent_config: Agent configuration
        """
        self.agent_config = agent_config
        self.base_tools = [SerperDevTool(), ScrapeWebsiteTool()]
        
    def activities_agent(self) -> Agent:
        """
        Create an agent that identifies optimal activities and sites to visit.
        
        Returns:
            Activities agent
        """
        return Agent(
            role="Activities & Sites Specialist",
            goal="Identify optimal activities and sites to visit in each city",
            backstory="""
            You are a travel activities expert with in-depth knowledge of attractions, 
            experiences, and hidden gems in destinations worldwide. You excel at creating 
            personalized activity recommendations that align with travelers' interests, 
            timeline, and constraints. You know how to balance must-see landmarks with 
            authentic local experiences, and you're skilled at optimizing activity 
            scheduling based on geography, opening hours, and crowd patterns.
            """,
            tools=self.base_tools,
            verbose=True
        )
    
    def accommodation_agent(self) -> Agent:
        """
        Create an agent that finds optimal accommodations.
        
        Returns:
            Accommodation agent
        """
        return Agent(
            role="Accommodation Specialist",
            goal="Find optimal accommodations in each city",
            backstory="""
            You are an accommodation expert with extensive knowledge of hotels, resorts, 
            vacation rentals, and other lodging options worldwide. You excel at matching 
            travelers with ideal accommodations based on their preferences, budget, and 
            location requirements. You know how to balance luxury, comfort, value, and 
            convenience to find the perfect place to stay in any destination.
            """,
            tools=self.base_tools + [AccommodationSearchTool()],
            verbose=True
        )
    
    def dining_agent(self) -> Agent:
        """
        Create an agent that recommends dining options.
        
        Returns:
            Dining agent
        """
        return Agent(
            role="Dining Specialist",
            goal="Recommend dining options in each city",
            backstory="""
            You are a culinary travel expert with a deep appreciation for global cuisines 
            and dining experiences. You have extensive knowledge of restaurants, food markets, 
            and culinary traditions around the world. You excel at recommending dining options 
            that showcase local specialties while accommodating dietary restrictions, budgets, 
            and ambiance preferences. You know how to create balanced meal recommendations 
            across a trip that offer variety and authentic food experiences.
            """,
            tools=self.base_tools,
            verbose=True
        )
    
    def local_transit_agent(self) -> Agent:
        """
        Create an agent that plans local transportation within each city.
        
        Returns:
            Local transit agent
        """
        return Agent(
            role="Local Transit Specialist",
            goal="Plan local transportation within each city",
            backstory="""
            You are a local transportation expert with comprehensive knowledge of public 
            transit systems, walking routes, bike-sharing services, and ride-hailing options 
            in cities worldwide. You excel at creating efficient transportation plans that 
            optimize travelers' time and budget while considering convenience and experience. 
            You understand the nuances of navigating unfamiliar cities and can recommend the 
            best transit options based on distance, time of day, weather, and other factors.
            """,
            tools=self.base_tools,
            verbose=True
        )
    
    def activities_task(
        self, 
        city_info: Dict[str, Any],
        arrival_date: str,
        departure_date: str,
        constraints: List[Constraint]
    ) -> Task:
        """
        Create a task for planning activities and sites to visit.
        
        Args:
            city_info: Information about the city
            arrival_date: Date of arrival in the city
            departure_date: Date of departure from the city
            constraints: List of applicable constraints
            
        Returns:
            Activities planning task
        """
        # Convert constraints to natural language for the agent
        constraints_text = "\n".join([
            f"- {c.to_natural_language()}" for c in constraints
        ])
        
        return Task(
            description=f"""
            Plan a comprehensive set of activities and points of interest to visit in 
            {city_info['name']}, {city_info['country']} during the stay from {arrival_date} 
            to {departure_date} (total of {city_info['days']} days).
            
            Key interests in this city include:
            {', '.join(city_info.get('key_attractions', ['To be determined']))}
            
            Constraints to consider:
            {constraints_text}
            
            For each day of the visit, recommend activities and points of interest that:
            
            1. Provide a balanced mix of popular attractions and hidden gems
            2. Are geographically clustered to minimize transit time
            3. Account for opening hours and peak times
            4. Align with user preferences and constraints
            5. Allow for a reasonable pace (not overscheduled)
            
            Your output should include:
            1. Daily activity plans with specific points of interest
            2. Estimated time needed for each activity
            3. Brief description of each attraction
            4. Logical order of activities based on geography and opening hours
            5. Alternative or optional activities
            
            Format your response as a JSON object with the following structure:
            {{
                "city": "{city_info['name']}, {city_info['country']}",
                "days": [
                    {{
                        "day": number,
                        "date": "YYYY-MM-DD",
                        "activities": [
                            {{
                                "name": "string",
                                "type": "string (museum, landmark, tour, etc.)",
                                "description": "string",
                                "location": "string",
                                "estimated_duration": "string",
                                "opening_hours": "string",
                                "estimated_cost": number,
                                "booking_required": boolean,
                                "booking_info": "string (if applicable)"
                            }}
                        ],
                        "alternative_activities": [
                            {{
                                "name": "string",
                                "reason_to_consider": "string"
                            }}
                        ],
                        "estimated_total_cost": number
                    }}
                ],
                "estimated_total_activities_cost": number,
                "constraints_addressed": [
                    "string"
                ],
                "general_notes": "string"
            }}
            """,
            agent=self.activities_agent(),
            expected_output="A detailed daily activities plan for the entire stay in the city."
        )
    
    def accommodation_task(
        self, 
        city_info: Dict[str, Any],
        arrival_date: str,
        departure_date: str,
        activity_plan: Dict[str, Any],
        constraints: List[Constraint]
    ) -> Task:
        """
        Create a task for finding accommodation options.
        
        Args:
            city_info: Information about the city
            arrival_date: Date of arrival in the city
            departure_date: Date of departure from the city
            activity_plan: The planned activities
            constraints: List of applicable constraints
            
        Returns:
            Accommodation search task
        """
        # Convert constraints to natural language for the agent
        constraints_text = "\n".join([
            f"- {c.to_natural_language()}" for c in constraints
        ])
        
        return Task(
            description=f"""
            Find optimal accommodation options in {city_info['name']}, {city_info['country']} 
            for the stay from {arrival_date} to {departure_date} (total of {city_info['days']} days).
            
            Consider the planned activities and their locations:
            {', '.join([day['activities'][0]['location'] for day in activity_plan['days']])}
            
            Constraints to consider:
            {constraints_text}
            
            Search for accommodations that:
            
            1. Are conveniently located near planned activities or public transportation
            2. Align with the user's budget constraints
            3. Offer amenities relevant to the user's preferences
            4. Have good reviews and ratings
            5. Are available for the specified dates
            
            Your output should include:
            1. At least 3 recommended accommodations with detailed information
            2. Pros and cons of each option
            3. Price comparison and value assessment
            4. Location benefits relative to planned activities
            5. Booking information and cancellation policies
            
            Format your response as a JSON object with the following structure:
            {{
                "city": "{city_info['name']}, {city_info['country']}",
                "stay_duration": {{
                    "check_in": "{arrival_date}",
                    "check_out": "{departure_date}",
                    "total_nights": number
                }},
                "accommodations": [
                    {{
                        "name": "string",
                        "type": "string (hotel, apartment, hostel, etc.)",
                        "location": "string",
                        "proximity_to_activities": "string",
                        "price_per_night": number,
                        "total_price": number,
                        "rating": number,
                        "amenities": [
                            "string"
                        ],
                        "pros": [
                            "string"
                        ],
                        "cons": [
                            "string"
                        ],
                        "booking_info": "string",
                        "cancellation_policy": "string"
                    }}
                ],
                "constraints_addressed": [
                    "string"
                ],
                "recommendation_rationale": "string"
            }}
            """,
            agent=self.accommodation_agent(),
            expected_output="A detailed list of accommodation options with comprehensive information and comparisons."
        )
    
    def dining_task(
        self, 
        city_info: Dict[str, Any],
        activity_plan: Dict[str, Any],
        constraints: List[Constraint]
    ) -> Task:
        """
        Create a task for recommending dining options.
        
        Args:
            city_info: Information about the city
            activity_plan: The planned activities
            constraints: List of applicable constraints
            
        Returns:
            Dining recommendations task
        """
        # Convert constraints to natural language for the agent
        constraints_text = "\n".join([
            f"- {c.to_natural_language()}" for c in constraints
        ])
        
        return Task(
            description=f"""
            Recommend dining options in {city_info['name']}, {city_info['country']} that 
            complement the planned activities for the {city_info['days']}-day visit.
            
            Constraints to consider:
            {constraints_text}
            
            For each day of the visit, recommend:
            
            1. Breakfast options (or include in accommodation if applicable)
            2. Lunch options near planned activities for that day
            3. Dinner options that showcase local cuisine and dining culture
            4. Snack or coffee break options if appropriate
            
            Your recommendations should:
            1. Include a variety of price points and dining styles
            2. Feature authentic local cuisine and specialties
            3. Be conveniently located relative to planned activities
            4. Have good reviews and ratings
            5. Align with any dietary constraints or preferences
            
            Your output should include:
            1. Daily dining recommendations tied to the activity schedule
            2. Information about each restaurant/venue
            3. Signature dishes or menu recommendations
            4. Price expectations and reservation requirements
            5. Cultural context about local dining customs if relevant
            
            Format your response as a JSON object with the following structure:
            {{
                "city": "{city_info['name']}, {city_info['country']}",
                "local_specialties": [
                    {{
                        "dish": "string",
                        "description": "string"
                    }}
                ],
                "daily_recommendations": [
                    {{
                        "day": number,
                        "date": "YYYY-MM-DD",
                        "meals": [
                            {{
                                "meal_type": "string (breakfast, lunch, dinner, snack)",
                                "venue": "string",
                                "cuisine": "string",
                                "price_range": "string",
                                "location": "string",
                                "proximity_to_activities": "string",
                                "recommended_dishes": [
                                    "string"
                                ],
                                "reservation_required": boolean,
                                "reservation_info": "string (if applicable)"
                            }}
                        ]
                    }}
                ],
                "dining_budget_estimate": {{
                    "daily": number,
                    "total": number
                }},
                "constraints_addressed": [
                    "string"
                ],
                "local_dining_customs": "string"
            }}
            """,
            agent=self.dining_agent(),
            expected_output="A comprehensive dining plan with recommendations for each day."
        )
    
    def local_transit_task(
        self, 
        city_info: Dict[str, Any],
        activity_plan: Dict[str, Any],
        accommodation_info: Dict[str, Any],
        constraints: List[Constraint]
    ) -> Task:
        """
        Create a task for planning local transportation.
        
        Args:
            city_info: Information about the city
            activity_plan: The planned activities
            accommodation_info: The selected accommodation
            constraints: List of applicable constraints
            
        Returns:
            Local transit planning task
        """
        # Convert constraints to natural language for the agent
        constraints_text = "\n".join([
            f"- {c.to_natural_language()}" for c in constraints
        ])
        
        return Task(
            description=f"""
            Plan optimal local transportation in {city_info['name']}, {city_info['country']} 
            for the {city_info['days']}-day visit, connecting the selected accommodation with 
            all planned activities.
            
            Accommodation location:
            {accommodation_info['accommodations'][0]['location']}
            
            Daily activity locations:
            {', '.join([day['activities'][0]['location'] for day in activity_plan['days']])}
            
            Constraints to consider:
            {constraints_text}
            
            Your transportation plan should:
            
            1. Recommend the most efficient way to travel between accommodation and activities
            2. Identify the best public transportation options (subway, bus, tram, etc.)
            3. Suggest when walking, cycling, or taxis/rideshares are preferable
            4. Include information on costs, tickets, and transit passes
            5. Consider factors like rush hour, weather, and safety
            
            Your output should include:
            1. Daily transportation plans aligned with activity schedules
            2. Specific route recommendations and transit lines
            3. Cost information and money-saving options (day passes, etc.)
            4. Time estimates for each journey
            5. Tips for navigating the local transportation system
            
            Format your response as a JSON object with the following structure:
            {{
                "city": "{city_info['name']}, {city_info['country']}",
                "transportation_overview": {{
                    "main_transit_options": [
                        {{
                            "mode": "string",
                            "description": "string",
                            "pros": "string",
                            "cons": "string"
                        }}
                    ],
                    "recommended_transit_passes": [
                        {{
                            "name": "string",
                            "coverage": "string",
                            "price": number,
                            "worth_it": boolean,
                            "where_to_buy": "string"
                        }}
                    ],
                    "transit_tips": [
                        "string"
                    ]
                }},
                "daily_transit_plans": [
                    {{
                        "day": number,
                        "date": "YYYY-MM-DD",
                        "journeys": [
                            {{
                                "from": "string",
                                "to": "string",
                                "recommended_mode": "string",
                                "route_details": "string",
                                "estimated_time": "string",
                                "estimated_cost": number,
                                "alternative_options": [
                                    "string"
                                ]
                            }}
                        ],
                        "daily_transit_cost": number
                    }}
                ],
                "estimated_total_transit_cost": number,
                "constraints_addressed": [
                    "string"
                ],
                "general_transit_notes": "string"
            }}
            """,
            agent=self.local_transit_agent(),
            expected_output="A detailed local transportation plan for navigating the city efficiently."
        )
    
    def create_within_city_crew(
        self, 
        city_info: Dict[str, Any],
        arrival_date: str,
        departure_date: str,
        constraints: List[Constraint]
    ) -> Crew:
        """
        Create a crew of within-city layer agents.
        
        Args:
            city_info: Information about the city
            arrival_date: Date of arrival in the city
            departure_date: Date of departure from the city
            constraints: List of applicable constraints
            
        Returns:
            Crew of within-city layer agents
        """
        # Note: In reality, these tasks would be executed in a sequential manner
        # with each task depending on the results of previous tasks
        
        # Create the activities task
        activities_task = self.activities_task(
            city_info,
            arrival_date,
            departure_date,
            constraints
        )
        
        return Crew(
            agents=[
                self.activities_agent(),
                self.accommodation_agent(),
                self.dining_agent(),
                self.local_transit_agent()
            ],
            tasks=[activities_task],
            verbose=True
        )