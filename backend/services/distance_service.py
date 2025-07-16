from typing import List, Dict, Tuple
import math
import asyncio
from models.domain import Place

class DistanceService:
    """Service for calculating distances between places"""
    
    def __init__(self, use_google_maps: bool = False):
        self.use_google_maps = use_google_maps
        # TODO: Add Google Maps API key from environment
    
    async def get_distance_matrix(self, places: List[Place]) -> List[List[float]]:
        """
        Calculate distance matrix between all places.
        Returns a 2D array where matrix[i][j] is the distance from place i to place j.
        """
        n = len(places)
        matrix = [[0.0] * n for _ in range(n)]
        
        if self.use_google_maps:
            # TODO: Implement Google Maps Distance Matrix API
            matrix = await self._get_google_maps_matrix(places)
        else:
            # Use Haversine formula for great circle distances
            for i in range(n):
                for j in range(n):
                    if i != j:
                        matrix[i][j] = self._haversine_distance(
                            places[i].latitude, places[i].longitude,
                            places[j].latitude, places[j].longitude
                        )
        
        return matrix
    
    def _haversine_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """
        Calculate the great circle distance between two points on Earth.
        Returns distance in kilometers.
        """
        # Convert latitude and longitude from degrees to radians
        lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
        
        # Haversine formula
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        
        # Radius of earth in kilometers
        r = 6371
        
        return c * r
    
    async def _get_google_maps_matrix(self, places: List[Place]) -> List[List[float]]:
        """
        Get distance matrix using Google Maps Distance Matrix API.
        TODO: Implement this when Google Maps integration is needed.
        """
        # Placeholder for Google Maps API integration
        # This would make API calls to Google Maps Distance Matrix API
        # and return driving distances/times
        raise NotImplementedError("Google Maps integration not yet implemented")
    
    def get_distance_between_places(self, place1: Place, place2: Place) -> float:
        """Get distance between two specific places"""
        return self._haversine_distance(
            place1.latitude, place1.longitude,
            place2.latitude, place2.longitude
        )