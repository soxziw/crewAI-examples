from typing import Type
from pydantic import BaseModel, Field
import os

# Mock BaseTool since we're using an older version of crewai
class BaseTool:
    """Mock BaseTool class for compatibility"""
    name = "Base Tool"
    description = "Base tool description"
    args_schema = None

    def _run(self, *args, **kwargs):
        raise NotImplementedError("Subclass must implement _run method")
        
    def run(self, *args, **kwargs):
        return self._run(*args, **kwargs)


class FlightSearchToolInput(BaseModel):
    """Input schema for FlightSearchTool."""
    departure_id: str = Field(..., description="3 letter airport code of the departure location.")
    arrival_id: str = Field(..., description="3 letter airport code of the arrival location.")
    outbound_date: str = Field(..., description="Date of the outbound travel in YYYY-MM-DD format.")
    return_date: str = Field(..., description="Date of the return travel in YYYY-MM-DD format.")

class FlightSearchTool(BaseTool):
    name: str = "Flight Search Tool"
    description: str = (
        "A tool to search for flights using the SerpAPI Google Flights API. Input should be a detailed description of the desired flight, including origin, destination, dates, and any preferences."
    )
    args_schema: Type[BaseModel] = FlightSearchToolInput

    def _run(self, departure_id: str, arrival_id: str, outbound_date: str, return_date: str) -> str:
        # Return mock data instead of actual API call
        return {
            "search_metadata": {
                "status": "Success",
                "engine": "google_flights",
                "processed_at": "2024-05-04T12:00:00Z"
            },
            "search_parameters": {
                "departure_id": departure_id,
                "arrival_id": arrival_id,
                "outbound_date": outbound_date,
                "return_date": return_date
            },
            "best_flights": [
                {
                    "price": "$750",
                    "airline": "United Airlines",
                    "flight_duration": "5h 30m",
                    "departure_time": "08:30",
                    "arrival_time": "14:00",
                    "stops": 0
                },
                {
                    "price": "$620",
                    "airline": "American Airlines",
                    "flight_duration": "6h 15m",
                    "departure_time": "10:45",
                    "arrival_time": "17:00",
                    "stops": 1
                }
            ],
            "other_flights": [
                {
                    "price": "$580",
                    "airline": "Delta",
                    "flight_duration": "7h 20m",
                    "departure_time": "13:15",
                    "arrival_time": "20:35",
                    "stops": 1
                }
            ]
        }