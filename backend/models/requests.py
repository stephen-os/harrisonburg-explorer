from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from models.domain import Place

class RouteRequest(BaseModel):
    """Request model for route calculation"""
    places: List[Place] = Field(..., description="List of places to visit", min_items=2)
    algorithm: str = Field(..., description="Algorithm to use for optimization")
    constraints: Optional[Dict[str, Any]] = Field(None, description="Optional constraints for optimization")
    options: Optional[Dict[str, Any]] = Field(None, description="Additional options")

    class Config:
        schema_extra = {
            "example": {
                "places": [
                    {
                        "id": "place_1",
                        "name": "New York Office",
                        "latitude": 40.7128,
                        "longitude": -74.0060,
                        "address": "123 Main St, New York, NY",
                        "metadata": {
                            "visit_duration": 30,
                            "priority": "high"
                        }
                    },
                    {
                        "id": "place_2", 
                        "name": "Boston Office",
                        "latitude": 42.3601,
                        "longitude": -71.0589,
                        "address": "456 Oak St, Boston, MA"
                    }
                ],
                "algorithm": "nearest_neighbor",
                "constraints": {
                    "start_location": "place_1",
                    "end_location": "place_1",
                    "max_distance": 500
                },
                "options": {
                    "optimize_for": "distance",
                    "include_return_trip": True
                }
            }
        }

class AlgorithmInfoRequest(BaseModel):
    """Request for algorithm information"""
    algorithm: str = Field(..., description="Algorithm name")

class HealthCheckRequest(BaseModel):
    """Health check request"""
    pass