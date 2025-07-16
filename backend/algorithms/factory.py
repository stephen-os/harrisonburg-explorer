from typing import Dict, Type, List
from .base import TSPAlgorithm
from .nearest_neighbor import NearestNeighborAlgorithm
from .genetic_algorithm import GeneticAlgorithm

class AlgorithmFactory:
    """Factory for creating TSP algorithm instances"""
    
    _algorithms: Dict[str, Type[TSPAlgorithm]] = {
        'nearest_neighbor': NearestNeighborAlgorithm,
        'genetic': GeneticAlgorithm,
    }
    
    @classmethod
    def create_algorithm(cls, name: str) -> TSPAlgorithm:
        """Create an algorithm instance by name"""
        if name not in cls._algorithms:
            available = list(cls._algorithms.keys())
            raise ValueError(f"Unknown algorithm: '{name}'. Available algorithms: {available}")
        
        return cls._algorithms[name]()
    
    @classmethod
    def get_available_algorithms(cls) -> List[str]:
        """Get list of available algorithm names"""
        return list(cls._algorithms.keys())
    
    @classmethod
    def register_algorithm(cls, name: str, algorithm_class: Type[TSPAlgorithm]):
        """Register a new algorithm"""
        if not issubclass(algorithm_class, TSPAlgorithm):
            raise ValueError("Algorithm class must inherit from TSPAlgorithm")
        cls._algorithms[name] = algorithm_class
        
    @classmethod
    def get_algorithm_info(cls, name: str) -> Dict[str, str]:
        """Get information about an algorithm"""
        if name not in cls._algorithms:
            raise ValueError(f"Unknown algorithm: '{name}'")
        
        algorithm = cls.create_algorithm(name)
        return {
            'name': algorithm.name(),
            'description': algorithm.description()
        }