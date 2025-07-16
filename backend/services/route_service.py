from typing import List, Dict, Any, Optional
import time
import uuid
from datetime import datetime

from models.domain import Place, Route, RouteSegment, OptimizationResult
from algorithms.factory import AlgorithmFactory
from services.distance_service import DistanceService
from services.validation_service import ValidationService

class RouteService:
    """Main service for route optimization"""
    
    def __init__(self):
        self.distance_service = DistanceService()
        self.validation_service = ValidationService()
    
    async def calculate_route(self, places: List[Place], algorithm_name: str, 
                            constraints: Optional[Dict[str, Any]] = None) -> OptimizationResult:
        """
        Calculate optimal route using specified algorithm.
        
        Args:
            places: List of places to visit
            algorithm_name: Name of algorithm to use
            constraints: Optional constraints for the optimization
            
        Returns:
            OptimizationResult with the optimized route
            
        Raises:
            ValueError: If input validation fails
        """
        # Validate inputs
        await self._validate_inputs(places, algorithm_name, constraints)
        
        # Start timing
        start_time = time.time()
        
        # Get distance matrix
        distance_matrix = await self.distance_service.get_distance_matrix(places)
        
        # Create algorithm instance
        algorithm = AlgorithmFactory.create_algorithm(algorithm_name)
        
        # Solve TSP
        route = algorithm.solve(places, distance_matrix, constraints)
        
        # Calculate computation time
        computation_time = time.time() - start_time
        
        # Enhance route with additional information
        enhanced_route = await self._enhance_route(route, places, distance_matrix, computation_time)
        
        # Calculate improvement (if applicable)
        improvement = self._calculate_improvement(distance_matrix, enhanced_route)
        
        return OptimizationResult(
            route=enhanced_route,
            improvement_percentage=improvement,
            iterations=1  # For nearest neighbor, only 1 iteration
        )
    
    async def _validate_inputs(self, places: List[Place], algorithm_name: str, 
                              constraints: Optional[Dict[str, Any]]) -> None:
        """Validate all inputs and raise ValueError if invalid"""
        
        # Validate places
        place_validation = self.validation_service.validate_places(places)
        if not place_validation['valid']:
            raise ValueError(f"Invalid places: {'; '.join(place_validation['errors'])}")
        
        # Validate algorithm
        algorithm_validation = self.validation_service.validate_algorithm(algorithm_name)
        if not algorithm_validation['valid']:
            raise ValueError(algorithm_validation['error'])
        
        # Validate constraints
        constraint_validation = self.validation_service.validate_constraints(constraints, places)
        if not constraint_validation['valid']:
            raise ValueError(f"Invalid constraints: {'; '.join(constraint_validation['errors'])}")
    
    async def _enhance_route(self, route: Route, places: List[Place], 
                           distance_matrix: List[List[float]], computation_time: float) -> Route:
        """Enhance route with additional information"""
        
        # Create place lookup
        place_lookup = {place.id: place for place in places}
        
        # Create route segments
        segments = []
        total_time = 0
        
        for i in range(len(route.places_order) - 1):
            from_place_id = route.places_order[i]
            to_place_id = route.places_order[i + 1]
            
            # Find place indices
            from_idx = next(j for j, p in enumerate(places) if p.id == from_place_id)
            to_idx = next(j for j, p in enumerate(places) if p.id == to_place_id)
            
            distance = distance_matrix[from_idx][to_idx]
            # Estimate time (assume 50 km/h average speed)
            duration = distance / 50 * 60  # Convert to minutes
            
            segments.append(RouteSegment(
                from_place_id=from_place_id,
                to_place_id=to_place_id,
                distance=distance,
                duration=duration
            ))
            
            total_time += duration
        
        # Update route with enhanced information
        route.id = str(uuid.uuid4())
        route.segments = segments
        route.total_time = total_time
        route.created_at = datetime.now()
        route.computation_time = computation_time
        
        return route
    
    def _calculate_improvement(self, distance_matrix: List[List[float]], route: Route) -> Optional[float]:
        """Calculate improvement percentage compared to random route"""
        if len(route.places_order) < 3:
            return None
        
        # Calculate average distance for random routes (approximation)
        n = len(distance_matrix)
        total_distances = sum(sum(row) for row in distance_matrix)
        avg_distance = total_distances / (n * n)
        random_route_distance = avg_distance * (n - 1)  # Approximate random route distance
        
        if random_route_distance > 0:
            improvement = ((random_route_distance - route.total_distance) / random_route_distance) * 100
            return max(0, improvement)  # Don't show negative improvements
        
        return None
    
    def get_available_algorithms(self) -> List[str]:
        """Get list of available algorithms"""
        return AlgorithmFactory.get_available_algorithms()
    
    def get_algorithm_info(self, algorithm_name: str) -> Dict[str, str]:
        """Get information about a specific algorithm"""
        try:
            algorithm = AlgorithmFactory.create_algorithm(algorithm_name)
            return {
                'name': algorithm.name(),
                'description': algorithm.description()
            }
        except ValueError:
            raise ValueError(f"Unknown algorithm: {algorithm_name}")