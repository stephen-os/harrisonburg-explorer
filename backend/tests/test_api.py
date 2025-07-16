import pytest
from fastapi.testclient import TestClient
from fastapi import FastAPI
from api.routes import router

# Create test app
app = FastAPI()
app.include_router(router)
client = TestClient(app)

class TestAPIRoutes:
    """Test cases for API routes"""
    
    def test_health_check(self):
        """Test health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert "algorithms_available" in data
        assert isinstance(data["algorithms_available"], list)
    
    def test_get_algorithms(self):
        """Test get algorithms endpoint"""
        response = client.get("/algorithms")
        assert response.status_code == 200
        
        data = response.json()
        assert "algorithms" in data
        assert isinstance(data["algorithms"], list)
        assert len(data["algorithms"]) > 0
        
        # Check algorithm structure
        algorithm = data["algorithms"][0]
        assert "name" in algorithm
        assert "description" in algorithm
    
    def test_get_algorithm_info_valid(self):
        """Test get algorithm info with valid algorithm"""
        response = client.get("/algorithms/nearest_neighbor")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert data["algorithm"] is not None
        assert data["algorithm"]["name"] == "nearest_neighbor"
    
    def test_get_algorithm_info_invalid(self):
        """Test get algorithm info with invalid algorithm"""
        response = client.get("/algorithms/nonexistent_algorithm")
        assert response.status_code == 200  # Returns 200 but with error in response
        
        data = response.json()
        assert data["success"] is False
        assert "error" in data
    
    def test_calculate_route_valid(self):
        """Test route calculation with valid request"""
        request_data = {
            "places": [
                {
                    "id": "place_1",
                    "name": "New York",
                    "latitude": 40.7128,
                    "longitude": -74.0060
                },
                {
                    "id": "place_2",
                    "name": "Boston", 
                    "latitude": 42.3601,
                    "longitude": -71.0589
                },
                {
                    "id": "place_3",
                    "name": "Philadelphia",
                    "latitude": 39.9526,
                    "longitude": -75.1652
                }
            ],
            "algorithm": "nearest_neighbor",
            "constraints": {
                "start_location": "place_1",
                "return_to_start": True
            }
        }
        
        response = client.post("/calculate-route", json=request_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert data["route"] is not None
        assert data["metadata"] is not None
        
        # Check route structure
        route = data["route"]
        assert "id" in route
        assert "places_order" in route
        assert "total_distance" in route
        assert "algorithm_used" in route
        assert route["algorithm_used"] == "nearest_neighbor"
        assert len(route["places_order"]) >= 3
        
        # Check metadata
        metadata = data["metadata"]
        assert "computation_time" in metadata
        assert "improvement_percentage" in metadata
    
    def test_calculate_route_invalid_algorithm(self):
        """Test route calculation with invalid algorithm"""
        request_data = {
            "places": [
                {
                    "id": "place_1",
                    "name": "New York",
                    "latitude": 40.7128,
                    "longitude": -74.0060
                },
                {
                    "id": "place_2",
                    "name": "Boston",
                    "latitude": 42.3601,
                    "longitude": -71.0589
                }
            ],
            "algorithm": "invalid_algorithm"
        }
        
        response = client.post("/calculate-route", json=request_data)
        assert response.status_code == 400
    
    def test_calculate_route_too_few_places(self):
        """Test route calculation with too few places"""
        request_data = {
            "places": [
                {
                    "id": "place_1",
                    "name": "New York",
                    "latitude": 40.7128,
                    "longitude": -74.0060
                }
            ],
            "algorithm": "nearest_neighbor"
        }
        
        response = client.post("/calculate-route", json=request_data)
        assert response.status_code == 400
    
    def test_calculate_route_invalid_coordinates(self):
        """Test route calculation with invalid coordinates"""
        request_data = {
            "places": [
                {
                    "id": "place_1",
                    "name": "Invalid Place",
                    "latitude": 200,  # Invalid latitude
                    "longitude": -74.0060
                },
                {
                    "id": "place_2",
                    "name": "Boston",
                    "latitude": 42.3601,
                    "longitude": -71.0589
                }
            ],
            "algorithm": "nearest_neighbor"
        }
        
        response = client.post("/calculate-route", json=request_data)
        assert response.status_code == 400
    
    def test_calculate_route_with_constraints(self):
        """Test route calculation with various constraints"""
        request_data = {
            "places": [
                {
                    "id": "place_1",
                    "name": "New York",
                    "latitude": 40.7128,
                    "longitude": -74.0060
                },
                {
                    "id": "place_2",
                    "name": "Boston",
                    "latitude": 42.3601,
                    "longitude": -71.0589
                },
                {
                    "id": "place_3",
                    "name": "Philadelphia",
                    "latitude": 39.9526,
                    "longitude": -75.1652
                }
            ],
            "algorithm": "nearest_neighbor",
            "constraints": {
                "start_location": "place_2",
                "end_location": "place_3",
                "max_distance": 1000
            }
        }
        
        response = client.post("/calculate-route", json=request_data)
        assert response.status_code == 200
        
        data = response.json()
        route = data["route"]
        
        # Should start with place_2 if specified
        assert route["places_order"][0] == "place_2"
    
    def test_calculate_route_malformed_json(self):
        """Test route calculation with malformed JSON"""
        response = client.post("/calculate-route", data="invalid json")
        assert response.status_code == 422
    
    def test_calculate_route_missing_required_fields(self):
        """Test route calculation with missing required fields"""
        request_data = {
            "places": [
                {
                    "id": "place_1",
                    "name": "New York",
                    "latitude": 40.7128,
                    "longitude": -74.0060
                }
            ]
            # Missing algorithm field
        }
        
        response = client.post("/calculate-route", json=request_data)
        assert response.status_code == 422

class TestAPIErrorHandling:
    """Test error handling in API"""
    
    def test_404_endpoint(self):
        """Test non-existent endpoint"""
        response = client.get("/nonexistent")
        assert response.status_code == 404
    
    def test_method_not_allowed(self):
        """Test wrong HTTP method"""
        response = client.put("/algorithms")
        assert response.status_code == 405

# Performance tests
class TestAPIPerformance:
    """Basic performance tests"""
    
    def test_calculate_route_performance(self):
        """Test route calculation performance with multiple places"""
        import time
        
        # Create a larger set of places
        places = []
        for i in range(10):
            places.append({
                "id": f"place_{i}",
                "name": f"Place {i}",
                "latitude": 40.0 + i * 0.1,
                "longitude": -74.0 + i * 0.1
            })
        
        request_data = {
            "places": places,
            "algorithm": "nearest_neighbor"
        }
        
        start_time = time.time()
        response = client.post("/calculate-route", json=request_data)
        end_time = time.time()
        
        assert response.status_code == 200
        assert (end_time - start_time) < 5.0  # Should complete within 5 seconds

if __name__ == "__main__":
    pytest.main([__file__])