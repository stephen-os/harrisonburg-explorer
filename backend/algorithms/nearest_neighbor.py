from typing import List, Dict, Any
from .base import TSPAlgorithm
from models.domain import Place, Route

class NearestNeighborAlgorithm(TSPAlgorithm):
    def name(self) -> str:
        return "nearest_neighbor"
    
    def description(self) -> str:
        return "Greedy nearest neighbor heuristic"
    
    def solve(self, places: List[Place], distance_matrix: List[List[float]], 
              constraints: Dict[str, Any] = None) -> Route:
        # Implementation here
        start_idx = 0  # or from constraints
        visited = [False] * len(places)
        route_order = [start_idx]
        visited[start_idx] = True
        
        current = start_idx
        total_distance = 0
        
        for _ in range(len(places) - 1):
            nearest_idx = self._find_nearest_unvisited(current, distance_matrix, visited)
            total_distance += distance_matrix[current][nearest_idx]
            route_order.append(nearest_idx)
            visited[nearest_idx] = True
            current = nearest_idx
        
        # Return to start if required
        if constraints and constraints.get('return_to_start', True):
            total_distance += distance_matrix[current][start_idx]
            route_order.append(start_idx)
        
        return Route(
            places_order=[places[i].id for i in route_order],
            total_distance=total_distance,
            algorithm_used=self.name()
        )
    
    def _find_nearest_unvisited(self, current: int, matrix: List[List[float]], 
                               visited: List[bool]) -> int:
        min_distance = float('inf')
        nearest_idx = -1
        
        for i in range(len(matrix)):
            if not visited[i] and matrix[current][i] < min_distance:
                min_distance = matrix[current][i]
                nearest_idx = i
        
        return nearest_idx