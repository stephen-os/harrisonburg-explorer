from typing import List, Dict, Any, Optional
from models.domain import Place
from algorithms.factory import AlgorithmFactory

class ValidationService:
    """Service for validating TSP requests"""
    
    def __init__(self):
        self.min_places = 2
        self.max_places = 100  # Reasonable limit for performance
    
    def validate_places(self, places: List[Place]) -> Dict[str, Any]:
        """
        Validate the list of places.
        Returns a dict with 'valid' boolean and 'errors' list.
        """
        errors = []
        
        # Check minimum number of places
        if len(places) < self.min_places:
            errors.append(f"Minimum {self.min_places} places required, got {len(places)}")
        
        # Check maximum number of places
        if len(places) > self.max_places:
            errors.append(f"Maximum {self.max_places} places allowed, got {len(places)}")
        
        # Check for duplicate place IDs
        place_ids = [place.id for place in places]
        if len(place_ids) != len(set(place_ids)):
            errors.append("Duplicate place IDs found")
        
        # Validate each place
        for i, place in enumerate(places):
            place_errors = self._validate_place(place, i)
            errors.extend(place_errors)
        
        return {
            'valid': len(errors) == 0,
            'errors': errors
        }
    
    def _validate_place(self, place: Place, index: int) -> List[str]:
        """Validate a single place"""
        errors = []
        
        # Check required fields
        if not place.id or not place.id.strip():
            errors.append(f"Place {index}: ID is required")
        
        if not place.name or not place.name.strip():
            errors.append(f"Place {index}: Name is required")
        
        # Validate coordinates
        if not (-90 <= place.latitude <= 90):
            errors.append(f"Place {index}: Invalid latitude {place.latitude}")
        
        if not (-180 <= place.longitude <= 180):
            errors.append(f"Place {index}: Invalid longitude {place.longitude}")
        
        return errors
    
    def validate_algorithm(self, algorithm_name: str) -> Dict[str, Any]:
        """Validate algorithm selection"""
        available_algorithms = AlgorithmFactory.get_available_algorithms()
        
        if algorithm_name not in available_algorithms:
            return {
                'valid': False,
                'error': f"Unknown algorithm '{algorithm_name}'. Available: {available_algorithms}"
            }
        
        return {'valid': True}
    
    def validate_constraints(self, constraints: Optional[Dict[str, Any]], 
                           places: List[Place]) -> Dict[str, Any]:
        """Validate constraints"""
        if not constraints:
            return {'valid': True}
        
        errors = []
        
        # Validate start location
        if 'start_location' in constraints:
            start_id = constraints['start_location']
            if not any(place.id == start_id for place in places):
                errors.append(f"Start location '{start_id}' not found in places")
        
        # Validate end location
        if 'end_location' in constraints:
            end_id = constraints['end_location']
            if not any(place.id == end_id for place in places):
                errors.append(f"End location '{end_id}' not found in places")
        
        # Validate numeric constraints
        if 'max_distance' in constraints:
            max_dist = constraints['max_distance']
            if not isinstance(max_dist, (int, float)) or max_dist <= 0:
                errors.append("max_distance must be a positive number")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors
        }