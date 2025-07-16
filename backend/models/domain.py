from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from datetime import datetime

class Place(BaseModel):
    id: str
    name: str
    latitude: float
    longitude: float
    address: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class RouteSegment(BaseModel):
    from_place_id: str
    to_place_id: str
    distance: float
    duration: Optional[float] = None
    directions: Optional[List[str]] = None

class Route(BaseModel):
    id: Optional[str] = None
    places_order: List[str]  # List of place IDs in order
    total_distance: float
    total_time: Optional[float] = None
    algorithm_used: str
    segments: Optional[List[RouteSegment]] = None
    metadata: Optional[Dict[str, Any]] = None
    created_at: Optional[datetime] = None
    computation_time: Optional[float] = None

class OptimizationResult(BaseModel):
    route: Route
    iterations: Optional[int] = None
    improvement_percentage: Optional[float] = None
    convergence_data: Optional[List[float]] = None