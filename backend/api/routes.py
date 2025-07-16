from fastapi import APIRouter, HTTPException, status
from datetime import datetime
from typing import List

from models.requests import RouteRequest, AlgorithmInfoRequest
from models.responses import (
    RouteResponse, AlgorithmsResponse, AlgorithmInfoResponse, 
    HealthCheckResponse, ErrorResponse, AlgorithmInfo
)
from services.route_service import RouteService

# Create router
router = APIRouter()

# Initialize services
route_service = RouteService()

@router.post("/calculate-route", 
             response_model=RouteResponse,
             status_code=status.HTTP_200_OK,
             summary="Calculate optimal route",
             description="Calculate the optimal route visiting all places using the specified algorithm")
async def calculate_route(request: RouteRequest) -> RouteResponse:
    """
    Calculate optimal route using TSP algorithms.
    
    - **places**: List of places to visit (minimum 2 places)
    - **algorithm**: Algorithm to use (e.g., 'nearest_neighbor')
    - **constraints**: Optional constraints like start/end locations
    - **options**: Additional optimization options
    """
    try:
        # Calculate the route
        result = await route_service.calculate_route(
            places=request.places,
            algorithm_name=request.algorithm,
            constraints=request.constraints
        )
        
        # Prepare metadata
        metadata = {
            "computation_time": result.route.computation_time,
            "improvement_percentage": result.improvement_percentage,
            "iterations": result.iterations
        }
        
        return RouteResponse(
            success=True,
            route=result.route,
            metadata=metadata
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )

@router.get("/algorithms",
            response_model=AlgorithmsResponse,
            summary="Get available algorithms",
            description="Retrieve list of all available TSP algorithms")
async def get_algorithms() -> AlgorithmsResponse:
    """
    Get all available TSP algorithms with their descriptions.
    """
    try:
        algorithm_names = route_service.get_available_algorithms()
        algorithms = []
        
        for name in algorithm_names:
            try:
                info = route_service.get_algorithm_info(name)
                algorithms.append(AlgorithmInfo(
                    name=info['name'],
                    description=info['description']
                ))
            except Exception:
                # Skip algorithms that fail to load
                continue
        
        return AlgorithmsResponse(algorithms=algorithms)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve algorithms: {str(e)}"
        )

@router.get("/algorithms/{algorithm_name}",
            response_model=AlgorithmInfoResponse,
            summary="Get algorithm information",
            description="Get detailed information about a specific algorithm")
async def get_algorithm_info(algorithm_name: str) -> AlgorithmInfoResponse:
    """
    Get information about a specific algorithm.
    
    - **algorithm_name**: Name of the algorithm (e.g., 'nearest_neighbor')
    """
    try:
        info = route_service.get_algorithm_info(algorithm_name)
        return AlgorithmInfoResponse(
            success=True,
            algorithm=AlgorithmInfo(
                name=info['name'],
                description=info['description']
            )
        )
        
    except ValueError as e:
        return AlgorithmInfoResponse(
            success=False,
            error=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get algorithm info: {str(e)}"
        )

@router.get("/health",
            response_model=HealthCheckResponse,
            summary="Health check",
            description="Check if the API is running and algorithms are available")
async def health_check() -> HealthCheckResponse:
    """
    Health check endpoint to verify service status.
    """
    try:
        algorithms = route_service.get_available_algorithms()
        
        return HealthCheckResponse(
            status="healthy",
            timestamp=datetime.now().isoformat(),
            algorithms_available=algorithms
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Service unhealthy: {str(e)}"
        )

# Error handlers
@router.get("/test-error",
            response_model=ErrorResponse,
            summary="Test error handling",
            description="Test endpoint for error handling (development only)")
async def test_error():
    """Test endpoint to verify error handling works correctly."""
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="This is a test error"
    )