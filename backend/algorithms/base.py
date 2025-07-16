from abc import ABC, abstractmethod
from typing import List, Dict, Any
from models.domain import Place, Route

class TSPAlgorithm(ABC):
    """Abstract base class for all TSP algorithms"""
    
    @abstractmethod
    def name(self) -> str:
        """Return algorithm name"""
        pass
    
    @abstractmethod
    def solve(self, places: List[Place], distance_matrix: List[List[float]], 
              constraints: Dict[str, Any] = None) -> Route:
        """Solve TSP problem and return optimized route"""
        pass
    
    @abstractmethod
    def description(self) -> str:
        """Return algorithm description"""
        pass
    
    def validate_input(self, places: List[Place]) -> bool:
        """Basic input validation"""
        return len(places) >= 2