from crewai import Agent, Crew, Process, Task

# Create mock classes for the missing parts in crewai 0.1.7
class CrewBase:
    """Mock CrewBase decorator"""
    def __init__(self, cls):
        self.cls = cls
    
    def __call__(self, *args, **kwargs):
        return self.cls(*args, **kwargs)

def after_kickoff(func):
    """Mock after_kickoff decorator"""
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper

def agent(func):
    """Mock agent decorator"""
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper

def crew(func):
    """Mock crew decorator"""
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper

def task(func):
    """Mock task decorator"""
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper

class CrewOutput:
    """Mock CrewOutput class"""
    def __init__(self, tasks_output=None):
        self.tasks_output = tasks_output or []
# Instead of importing from crewai_tools, we'll create a mock implementation
# from crewai_tools import SerperDevTool
# from crewai_tools import ScrapeWebsiteTool
import json

# Create mock tool classes to replace the missing crewai_tools
class SerperDevTool:
    """Mock implementation of SerperDevTool for development purposes."""
    def __init__(self):
        self.name = "SerperDevTool"
        
    def __call__(self, query):
        return f"Mock search results for: {query}"

class ScrapeWebsiteTool:
    """Mock implementation of ScrapeWebsiteTool for development purposes."""
    def __init__(self):
        self.name = "ScrapeWebsiteTool"
        
    def __call__(self, url):
        return f"Mock scraped content from: {url}"

try:
    # When installed as a package
    from trip_planner.tools.flight_search_tool import FlightSearchTool
    from trip_planner.tools.accommodation_search_tool import AccommodationSearchTool
    from trip_planner.tools.constraint_parser_tool import ConstraintParserTool
    from trip_planner.tools.constraint_verification_tool import ConstraintVerificationTool
    from trip_planner.maia_architecture import Constraint, TravelPlan
except ImportError:
    # When running directly from source
    from src.trip_planner.tools.flight_search_tool import FlightSearchTool
    from src.trip_planner.tools.accommodation_search_tool import AccommodationSearchTool
    from src.trip_planner.tools.constraint_parser_tool import ConstraintParserTool
    from src.trip_planner.tools.constraint_verification_tool import ConstraintVerificationTool
    from src.trip_planner.maia_architecture import Constraint, TravelPlan


@CrewBase
class TripPlanner():
    """TripPlanner crew"""

    @after_kickoff
    def process_results(self, result: CrewOutput) -> CrewOutput:
        print(result.tasks_output)

        outputs = {}

        for task_output in result.tasks_output:
            outputs[task_output.name] = task_output
        
        final_result = f"""
{outputs['report_generation_task']}
***

# Travel Options

{outputs['travel_options_task']}

***

# Accommodation

{outputs['accommodation_search_task']}

***

# Daily Itinerary

{outputs['itinerary_planning_task']}

        """

        with open('trip_report.md', 'w') as f:
            f.write(final_result)

        return final_result

    @agent
    def destination_researcher(self) -> Agent:
        return Agent(
            config=self.agents_config['destination_researcher'],
            tools=[SerperDevTool(), ScrapeWebsiteTool()],
        )

    @agent
    def travel_options_researcher(self) -> Agent:
        return Agent(
            config=self.agents_config['travel_options_researcher'],
            tools=[SerperDevTool(), ScrapeWebsiteTool(), FlightSearchTool()],
        )

    @agent
    def accommodation_researcher(self) -> Agent:
        return Agent(
            config=self.agents_config['accommodation_researcher'],
            tools=[SerperDevTool(), ScrapeWebsiteTool(), AccommodationSearchTool()],
        )

    @agent
    def itinerary_planner(self) -> Agent:
        return Agent(
            config=self.agents_config['itinerary_planner'],
            tools=[SerperDevTool(), ScrapeWebsiteTool()],
        )
    
    @agent
    def report_generator(self) -> Agent:
        return Agent(
            config=self.agents_config['report_generator'],
        )
    
    @agent
    def constraint_verifier(self) -> Agent:
        """
        New agent that verifies constraints are met throughout the travel planning process.
        """
        return Agent(
            role="Constraint Verification Specialist",
            goal="Ensure all user constraints are strictly enforced in the travel plan",
            backstory="""
            You are a meticulous travel plan auditor with exceptional attention to detail. 
            Your expertise lies in analyzing travel itineraries to ensure they strictly 
            adhere to all specified constraints and requirements. You can identify discrepancies, 
            inconsistencies, or constraint violations that others might miss. Your verification 
            process is thorough and systematic, and you provide clear feedback on any issues found.
            """,
            tools=[ConstraintParserTool(), ConstraintVerificationTool()],
            verbose=True
        )


    @task
    def destination_research_task(self) -> Task:
        return Task(
            config=self.tasks_config['destination_research_task'],
        )

    @task
    def travel_options_task(self) -> Task:
        return Task(
            config=self.tasks_config['travel_options_task'],
            output_file='1_travel_options.md',
        )

    @task
    def accommodation_search_task(self) -> Task:
        return Task(
            config=self.tasks_config['accommodation_search_task'],
            output_file='2_accommodation.md',
        )

    @task
    def itinerary_planning_task(self) -> Task:
        return Task(
            config=self.tasks_config['itinerary_planning_task'],
            output_file='3_itinerary_plan.md',
        )

    @task
    def report_generation_task(self) -> Task:
        return Task(
            config=self.tasks_config['report_generation_task'],
            output_file='4_trip_report.md',
        )
    
    @task
    def constraint_extraction_task(self) -> Task:
        """
        New task that extracts constraints from user inputs.
        """
        return Task(
            description="""
            Extract all constraints from the user's travel request and related inputs.
            Constraints may include budget limitations, time restrictions, accessibility 
            requirements, personal preferences, logistical constraints, etc.
            
            User inputs:
            - Destination: {destination_location}
            - Timeline: {travel_timeline}
            - Origin: {origin_location}
            - Additional constraints: {constraints}
            - Preferences: {preferences}
            
            Your output should categorize each identified constraint and specify whether
            it is a hard constraint (must be satisfied) or a soft constraint (preference).
            
            Format your response as a JSON array of constraint objects with the following structure:
            [
                {
                    "type": "budget|time|preference|logistics|accessibility|safety",
                    "description": "Clear description of the constraint",
                    "value": "Numeric or string value (if applicable)",
                    "is_hard_constraint": true|false,
                    "layer": "area|city|within_city|verification"
                }
            ]
            """,
            agent=self.constraint_verifier(),
            expected_output="A comprehensive JSON list of all extracted constraints from user inputs."
        )
    
    @task
    def plan_verification_task(self) -> Task:
        """
        New task that verifies the complete travel plan against all constraints.
        """
        return Task(
            description="""
            Verify that the complete travel plan satisfies all user constraints.
            
            You will receive:
            1. The complete travel plan (destination, travel options, accommodation, itinerary)
            2. The list of user constraints previously extracted
            
            Your task is to:
            1. Check each constraint against the relevant parts of the travel plan
            2. Identify any violations or potential issues
            3. Assess the severity of each violation (critical vs. minor)
            4. Suggest possible solutions or alternatives for any violations
            
            Format your response as a detailed verification report that includes:
            1. A summary of constraints checked
            2. Pass/fail status for each constraint
            3. Details of any violations found
            4. Recommended adjustments to make the plan fully compliant
            5. Overall assessment of the plan's adherence to user constraints
            
            This verification is crucial to ensure the final travel plan meets all user requirements.
            """,
            agent=self.constraint_verifier(),
            context=[
                "destination_research_task",
                "travel_options_task",
                "accommodation_search_task",
                "itinerary_planning_task",
                "constraint_extraction_task"
            ],
            expected_output="A detailed verification report assessing the travel plan's compliance with all user constraints."
        )


    @crew
    def crew(self) -> Crew:
        """Creates the TripPlanner crew"""
        
        # For constraint-aware processing, we need to determine if constraints are provided
        has_constraints = False
        if hasattr(self, 'inputs') and self.inputs:
            has_constraints = 'constraints' in self.inputs or 'preferences' in self.inputs
        
        # Base crew - original agents and tasks
        base_agents = [
            self.destination_researcher(),
            self.travel_options_researcher(),
            self.accommodation_researcher(),
            self.itinerary_planner(),
            self.report_generator()
        ]
        
        base_tasks = [
            self.destination_research_task(),
            self.travel_options_task(),
            self.accommodation_search_task(),
            self.itinerary_planning_task(),
            self.report_generation_task()
        ]
        
        # Add constraint-aware agents and tasks if constraints are provided
        if has_constraints:
            base_agents.append(self.constraint_verifier())
            
            # Insert constraint extraction as the first task
            base_tasks.insert(0, self.constraint_extraction_task())
            
            # Add verification as the second-to-last task (before report generation)
            base_tasks.insert(-1, self.plan_verification_task())
        
        return Crew(
            agents=base_agents,
            tasks=base_tasks,
            process=Process.sequential,
            verbose=True,
        )
    
    # Add support for new MAIA hierarchical processing
    def maia_crew(self) -> Crew:
        """Creates a MAIA hierarchical crew for constraint-aware travel planning"""
        from trip_planner.maia_orchestrator import MAIAOrchestrator
        
        # Initialize MAIA orchestrator
        orchestrator = MAIAOrchestrator()
        
        # Define a wrapper agent to interface with the orchestrator
        maia_agent = Agent(
            role="MAIA Travel Planning System",
            goal="Coordinate hierarchical travel planning with strict constraint enforcement",
            backstory="""
            You are MAIA (Multi-Agent Itinerary Assistant), an advanced travel planning 
            system that uses a hierarchical approach to create comprehensive travel plans 
            that strictly adhere to user constraints. You coordinate multiple specialized 
            agents across different planning layers, ensuring all aspects of the trip are 
            optimized and all constraints are satisfied.
            """,
            verbose=True
        )
        
        # Create a task that interfaces with the orchestrator
        maia_task = Task(
            description="""
            Create a comprehensive travel plan using the MAIA hierarchical planning system.
            
            User request:
            Destination: {destination_location}
            Timeline: {travel_timeline}
            Origin: {origin_location}
            Constraints: {constraints}
            Preferences: {preferences}
            
            Using the MAIA orchestrator, create a travel plan that strictly enforces 
            all user constraints through hierarchical planning:
            
            1. Area Layer: Select optimal destination region and timeframe
            2. City Layer: Select cities, durations, and inter-city transit
            3. Within-City Layer: Plan activities, accommodations, dining, local transit
            4. Verification Layer: Ensure all constraints are satisfied
            
            Your output should be a complete JSON travel plan with all details from all layers.
            """,
            agent=maia_agent,
            expected_output="A comprehensive JSON travel plan generated by the MAIA hierarchical planning system."
        )
        
        return Crew(
            agents=[maia_agent],
            tasks=[maia_task],
            process=Process.sequential,
            verbose=True,
        )