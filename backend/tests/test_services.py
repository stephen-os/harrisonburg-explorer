import pytest
from typing import List
from models.domain import Place
from services.distance_service import DistanceService
from services.validation_service import ValidationService
from services.route_service import RouteService

# Test fixtures
@pytest.fixture
def sample_places() -> List[Place]:
    """Sample places for testing"""
    return [
        Place(
            id="place_1",
            name="New York",
            latitude=40.7128,
            longitude=-74.0060
        ),
        Place(
            id="place_2", 
            name="Boston",
            latitude=42.3601,
            longitude=-71.0589
        ),
        Place(
            id="place_3",
            name="Philadelphia", 
            latitude=39.9526,
            longitude=-75.1652
        )
    ]

@pytest.fixture
def distance_service():
    """Distance service fixture"""
    return DistanceService()

@pytest.fixture
def validation_service():
    """Validation service fixture"""
    return ValidationService()

@pytest.fixture
def route_service():
    """Route service fixture"""
    return RouteService()

class TestDistanceService:
    """Test cases for DistanceService"""
    
    def test_haversine_distance_known_cities(self, distance_service):
        """Test haversine distance calculation between known cities"""
        # NYC to Boston is approximately 306 km
        distance = distance_service._haversine_distance(40.7128, -74.0060, 42.3601, -71.0589)
        assert 300 < distance < 320  # Allow some margin for rounding
    
    def test_haversine_distance_same_point(self, distance_service):
        """Test distance from a point to itself"""
        distance = distance_service._haversine_distance(40.7128, -74.0060, 40.7128, -74.0060)
        assert distance == 0
    
    @pytest.mark.asyncio
    async def test_get_distance_matrix(self, distance_service, sample_places):
        """Test distance matrix calculation"""
        matrix = await distance_service.get_distance_matrix(sample_places)
        
        # Check matrix dimensions
        assert len(matrix) == len(sample_places)
        assert all(len(row) == len(sample_places) for row in matrix)
        
        # Check diagonal is zero
        for i in range(len(matrix)):
            assert matrix[i][i] == 0
        
        # Check symmetry (distances should be same both ways)
        for i in range(len(matrix)):
            for j in range(len(matrix)):
                assert abs(matrix[i][j] - matrix[j][i]) < 0.001
    
    def test_get_distance_between_places(self, distance_service, sample_places):
        """Test distance calculation between two places"""
        distance = distance_service.get_distance_between_places(sample_places[0], sample_places[1])
        assert distance > 0
        assert isinstance(distance, float)

class TestValidationService:
    """Test cases for ValidationService"""
    
    def test_validate_places_valid(self, validation_service, sample_places):
        """Test validation with valid places"""
        result = validation_service.validate_places(sample_places)
        assert result['valid'] is True
        assert len(result['errors']) == 0
    
    def test_validate_places_too_few(self, validation_service):
        """Test validation with too few places"""
        places = [Place(id="1", name="Place 1", latitude=0, longitude=0)]
        result = validation_service.validate_places(places)
        assert result['valid'] is False
        assert any("Minimum" in error for error in result['errors'])
    
    def test_validate_places_duplicate_ids(self, validation_service):
        """Test validation with duplicate place IDs"""
        places = [
            Place(id="same_id", name="Place 1", latitude=0, longitude=0),
            Place(id="same_id", name="Place 2", latitude=1, longitude=1)
        ]
        result = validation_service.validate_places(places)
        assert result['valid'] is False
        assert any("Duplicate" in error for error in result['errors'])
    
    def test_validate_places_invalid_coordinates(self, validation_service):
        """Test validation with invalid coordinates"""
        places = [
            Place(id="1", name="Invalid Lat", latitude=100, longitude=0),  # Invalid lat
            Place(id="2", name="Invalid Lon", latitude=0, longitude=200)   # Invalid lon
        ]
        result = validation_service.validate_places(places)
        assert result['valid'] is False
        assert any("latitude" in error for error in result['errors'])
        assert any("longitude" in error for error in result['errors'])
    
    def test_validate_algorithm_valid(self, validation_service):
        """Test validation with valid algorithm"""
        result = validation_service.validate_algorithm("nearest_neighbor")
        assert result['valid'] is True
    
    def test_validate_algorithm_invalid(self, validation_service):
        """Test validation with invalid algorithm"""
        result = validation_service.validate_algorithm("nonexistent_algorithm")
        assert result['valid'] is False
        assert "Unknown algorithm" in result['error']
    
    def test_validate_constraints_valid(self, validation_service, sample_places):
        """Test validation with valid constraints"""
        constraints = {
            "start_location": "place_1",
            "end_location": "place_2",
            "max_distance": 1000
        }
        result = validation_service.validate_constraints(constraints, sample_places)
        assert result['valid'] is True
    
    def test_validate_constraints_invalid_location(self, validation_service, sample_places):
        """Test validation with invalid start/end location"""
        constraints = {"start_location": "nonexistent_place"}
        result = validation_service.validate_constraints(constraints, sample_places)
        assert result['valid'] is False
        assert any("not found" in error for error in result['errors'])

class TestRouteService:
    """Test cases for RouteService"""
    
    @pytest.mark.asyncio
    async def test_calculate_route_valid(self, route_service, sample_places):
        """Test route calculation with valid inputs"""
        result = await route_service.calculate_route(
            places=sample_places,
            algorithm_name="nearest_neighbor"
        )
        
        assert result.route is not None
        assert result.route.algorithm_used == "nearest_neighbor"
        assert len(result.route.places_order) >= len(sample_places)
        assert result.route.total_distance > 0
        assert result.route.computation_time is not None
    
    @pytest.mark.asyncio
    async def test_calculate_route_invalid_algorithm(self, route_service, sample_places):
        """Test route calculation with invalid algorithm"""
        with pytest.raises(ValueError, match="Unknown algorithm"):
            await route_service.calculate_route(
                places=sample_places,
                algorithm_name="invalid_algorithm"
            )
    
    @pytest.mark.asyncio
    async def test_calculate_route_invalid_places(self, route_service):
        """Test route calculation with invalid places"""
        invalid_places = [Place(id="1", name="Place 1", latitude=0, longitude=0)]  # Only 1 place
        
        with pytest.raises(ValueError, match="Minimum"):
            await route_service.calculate_route(
                places=invalid_places,
                algorithm_name="nearest_neighbor"
            )
    
    def test_get_available_algorithms(self, route_service):
        """Test getting available algorithms"""
        algorithms = route_service.get_available_algorithms()
        assert isinstance(algorithms, list)
        assert len(algorithms) > 0
        assert "nearest_neighbor" in algorithms
    
    def test_get_algorithm_info_valid(self, route_service):
        """Test getting algorithm info for valid algorithm"""
        info = route_service.get_algorithm_info("nearest_neighbor")
        assert "name" in info
        assert "description" in info
        assert info["name"] == "nearest_neighbor"
    
    def test_get_algorithm_info_invalid(self, route_service):
        """Test getting algorithm info for invalid algorithm"""
        with pytest.raises(ValueError, match="Unknown algorithm"):
            route_service.get_algorithm_info("invalid_algorithm")

# Integration tests
class TestServiceIntegration:
    """Integration tests for services working together"""
    
    @pytest.mark.asyncio
    async def test_full_route_calculation_flow(self, sample_places):
        """Test complete flow from request to response"""
        route_service = RouteService()
        
        # Test with constraints
        constraints = {
            "start_location": "place_1",
            "return_to_start": True
        }
        
        result = await route_service.calculate_route(
            places=sample_places,
            algorithm_name="nearest_neighbor",
            constraints=constraints
        )
        
        # Verify result structure
        assert result.route.id is not None
        assert result.route.segments is not None
        assert len(result.route.segments) > 0
        assert result.route.places_order[0] == "place_1"  # Should start at place_1
        assert result.route.total_time is not None
        assert result.improvement_percentage is not None

if __name__ == "__main__":
    pytest.main([__file__])