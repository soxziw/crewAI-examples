from typing import Type
from pydantic import BaseModel, Field
import os

# Import our mock BaseTool
from src.trip_planner.tools.flight_search_tool import BaseTool


class AccommodationSearchToolInput(BaseModel):
    """Input schema for AccommodationSearchTool."""
    location: str = Field(..., description="Location to search for accommodations.")
    checkin_date: str = Field(..., description="Date of the check-in in YYYY-MM-DD format.")
    checkout_date: str = Field(..., description="Date of the check-out in YYYY-MM-DD format.")


class AccommodationSearchTool(BaseTool):
    name: str = "Accommodation Search Tool"
    description: str = (
        "A tool to search for accommodations using the SerpAPI Google Accommodation API. Input should be a detailed description of the desired accommodation, including location, and dates."
    )
    args_schema: Type[BaseModel] = AccommodationSearchToolInput

    def _run(self, location: str, checkin_date: str, checkout_date: str) -> str:
        # Return mock data instead of actual API call
        return {
            "search_metadata": {
                "status": "Success",
                "engine": "google_hotels",
                "processed_at": "2024-05-04T12:30:00Z"
            },
            "search_parameters": {
                "location": location,
                "checkin_date": checkin_date,
                "checkout_date": checkout_date
            },
            "hotels": [
                {
                    "name": "Grand Hotel",
                    "rating": 4.5,
                    "reviews": 1250,
                    "price_per_night": "$180",
                    "address": f"123 Main St, {location}",
                    "amenities": ["Free WiFi", "Swimming Pool", "Fitness Center"],
                    "distance_to_center": "0.5 miles"
                },
                {
                    "name": "Budget Inn",
                    "rating": 3.8,
                    "reviews": 820,
                    "price_per_night": "$95",
                    "address": f"456 Oak Ave, {location}",
                    "amenities": ["Free WiFi", "Free Breakfast", "Parking"],
                    "distance_to_center": "1.2 miles"
                },
                {
                    "name": "Luxury Suites",
                    "rating": 4.8,
                    "reviews": 650,
                    "price_per_night": "$350",
                    "address": f"789 Park Blvd, {location}",
                    "amenities": ["Free WiFi", "Spa", "Pool", "Room Service", "Restaurant"],
                    "distance_to_center": "0.2 miles"
                }
            ]
        }