"""
Area Layer Agents for MAIA

These agents handle the highest level of planning, focusing on:
1. Destination region selection
2. Overall timeframe planning
3. High-level constraint processing
"""

from crewai import Agent, Task, Crew
# Instead of importing from crewai_tools, use our mock implementation
from typing import Dict, Any, List

# Import the mock tools from crew.py
try:
    from trip_planner.crew import SerperDevTool, ScrapeWebsiteTool
    from trip_planner.maia_architecture import AgentLayer, Constraint
    from trip_planner.tools.constraint_parser_tool import ConstraintParserTool
except ImportError:
    from src.trip_planner.crew import SerperDevTool, ScrapeWebsiteTool
    from src.trip_planner.maia_architecture import AgentLayer, Constraint
    from src.trip_planner.tools.constraint_parser_tool import ConstraintParserTool


class AreaLayerAgents:
    """
    Area Layer agents that handle high-level destination and timeframe planning.
    """
    
    def __init__(self, agent_config: Dict[str, Any]):
        """
        Initialize the Area Layer agents.
        
        Args:
            agent_config: Agent configuration
        """
        self.agent_config = agent_config
        self.tools = [SerperDevTool(), ScrapeWebsiteTool(), ConstraintParserTool()]
        
    def destination_selector_agent(self) -> Agent:
        """
        Create an agent that selects optimal destination regions based on constraints.
        
        Returns:
            Destination selection agent
        """
        return Agent(
            role="Destination Region Specialist",
            goal="Select the optimal destination region and timeframe based on user constraints",
            backstory="""
            You are a travel expert with extensive knowledge of global destinations, 
            seasonal travel patterns, and regional logistics. You excel at matching 
            travelers with ideal regions based on their preferences, timeline, and 
            constraints. You consider factors like climate, local events, tourist 
            traffic, and geopolitical situations when making recommendations.
            """,
            tools=self.tools,
            verbose=True
        )
    
    def destination_selection_task(
        self, 
        user_request: str,
        constraints: List[Constraint]
    ) -> Task:
        """
        Create a task for destination region selection.
        
        Args:
            user_request: User's travel request
            constraints: List of applicable constraints
            
        Returns:
            Destination selection task
        """
        # Convert constraints to natural language for the agent
        constraints_text = "\n".join([
            f"- {c.to_natural_language()}" for c in constraints
        ])
        
        return Task(
            description=f"""
            Based on the user's request and constraints, select the optimal destination 
            region and suggest a timeframe for travel. Consider all constraints carefully
            and explain your reasoning.
            
            User request: {user_request}
            
            Constraints to consider:
            {constraints_text}
            
            Your output should include:
            1. Recommended destination region(s)
            2. Suggested timeframe (specific dates if possible)
            3. Reasoning for your recommendations
            4. Any potential conflicts with the provided constraints
            5. Alternative suggestions if there are irreconcilable constraints
            
            Format your response as a JSON object with the following structure:
            {{
                "destination_region": "string",
                "timeframe": {{
                    "start_date": "YYYY-MM-DD",
                    "end_date": "YYYY-MM-DD",
                    "total_days": number
                }},
                "reasoning": "string",
                "constraint_conflicts": [
                    {{
                        "constraint": "string",
                        "conflict": "string",
                        "resolution": "string"
                    }}
                ],
                "alternatives": [
                    {{
                        "destination_region": "string",
                        "timeframe": {{
                            "start_date": "YYYY-MM-DD",
                            "end_date": "YYYY-MM-DD"
                        }},
                        "reasoning": "string"
                    }}
                ]
            }}
            """,
            agent=self.destination_selector_agent(),
            expected_output="A comprehensive destination region selection with timeframe recommendations based on constraints."
        )
    
    def timeframe_optimization_task(
        self, 
        destination_region: str,
        preliminary_timeframe: Dict[str, Any],
        constraints: List[Constraint]
    ) -> Task:
        """
        Create a task for optimizing the travel timeframe.
        
        Args:
            destination_region: Selected destination region
            preliminary_timeframe: Initial timeframe recommendation
            constraints: List of applicable constraints
            
        Returns:
            Timeframe optimization task
        """
        # Convert constraints to natural language for the agent
        constraints_text = "\n".join([
            f"- {c.to_natural_language()}" for c in constraints
        ])
        
        return Task(
            description=f"""
            Optimize the travel timeframe for {destination_region} based on the preliminary 
            recommendation and constraints. Consider factors like:
            
            1. Seasonal weather patterns
            2. Local events and festivals
            3. Tourist high/low seasons
            4. Pricing fluctuations
            5. Availability of key attractions
            
            Preliminary timeframe:
            Start date: {preliminary_timeframe['start_date']}
            End date: {preliminary_timeframe['end_date']}
            Total days: {preliminary_timeframe['total_days']}
            
            Constraints to consider:
            {constraints_text}
            
            Your output should include:
            1. Optimized travel dates with justification
            2. Recommended trip duration (if different from preliminary)
            3. Specific seasonal considerations
            4. Impacts on cost and availability
            5. Any constraints that were considered in your optimization
            
            Format your response as a JSON object with the following structure:
            {{
                "optimized_timeframe": {{
                    "start_date": "YYYY-MM-DD",
                    "end_date": "YYYY-MM-DD",
                    "total_days": number
                }},
                "justification": "string",
                "seasonal_factors": [
                    {{
                        "factor": "string",
                        "impact": "string"
                    }}
                ],
                "cost_impacts": {{
                    "description": "string",
                    "estimated_difference": "string"
                }},
                "constraints_addressed": [
                    "string"
                ]
            }}
            """,
            agent=self.destination_selector_agent(),  # Reuse the same agent
            expected_output="An optimized travel timeframe with detailed justification and seasonal considerations."
        )
    
    def create_area_crew(
        self, 
        user_request: str,
        constraints: List[Constraint]
    ) -> Crew:
        """
        Create a crew of area layer agents.
        
        Args:
            user_request: User's travel request
            constraints: List of applicable constraints
            
        Returns:
            Crew of area layer agents
        """
        # Create the destination selection task
        dest_selection_task = self.destination_selection_task(user_request, constraints)
        
        return Crew(
            agents=[self.destination_selector_agent()],
            tasks=[dest_selection_task],
            verbose=True
        )