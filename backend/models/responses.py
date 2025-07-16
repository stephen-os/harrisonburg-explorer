from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from models.domain import Route, OptimizationResult

class RouteResponse(BaseModel):
    """Response model for route calculation"""
    success: bool
    route: Optional[Route] = None
    metadata: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

    class Config:
        schema_extra = {
            "example": {
                "success": True,
                "route": {
                    "id": "route_12345",
                    "places_order": ["place_1", "place_2", "place_1"],
                    "total_distance": 245.7,
                    "total_time": 180,
                    "algorithm_used": "nearest_neighbor",
                    "segments": [
                        {
                            "from_place_id": "place_1",
                            "to_place_id": "place_2",
                            "distance": 122.85,
                            "duration": 90
                        }
                    ]
                },
                "metadata": {
                    "computation_time": 0.123,
                    "improvement_percentage": 23.4
                }
            }
        }

class AlgorithmInfo(BaseModel):
    """Information about an algorithm"""
    name: str
    description: str

class AlgorithmsResponse(BaseModel):
    """Response with available algorithms"""
    algorithms: List[AlgorithmInfo]

class AlgorithmInfoResponse(BaseModel):
    """Response with specific algorithm info"""
    success: bool
    algorithm: Optional[AlgorithmInfo] = None
    error: Optional[str] = None

class HealthCheckResponse(BaseModel):
    """Health check response"""
    status: str
    timestamp: str
    version: str = "1.0.0"
    algorithms_available: List[str]

class ErrorResponse(BaseModel):
    """Standard error response"""
    success: bool = False
    error: str
    details: Optional[Dict[str, Any]] = None