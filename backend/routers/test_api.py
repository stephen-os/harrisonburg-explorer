# backend/routers/test_api.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
import httpx
import os

router = APIRouter()

# Google API configuration
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Models for testing
class TestLocation(BaseModel):
    name: str
    address: str

class TestResult(BaseModel):
    test_name: str
    success: bool
    response_data: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    execution_time_ms: float
    timestamp: str

@router.get("/status")
async def api_test_status():
    """Check if Google API key is configured"""
    return {
        "google_api_configured": bool(GOOGLE_API_KEY),
        "api_key_preview": f"{GOOGLE_API_KEY[:10]}..." if GOOGLE_API_KEY else None,
        "project": "Harrisonburg Explorer",
        "timestamp": datetime.now().isoformat()
    }

@router.get("/geocoding")
async def test_geocoding():
    """Test Geocoding API with Harrisonburg locations"""
    if not GOOGLE_API_KEY:
        raise HTTPException(status_code=500, detail="Google API key not configured")
    
    start_time = datetime.now()
    # Test with a local Harrisonburg address
    test_address = "James Madison University, Harrisonburg, VA"
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://maps.googleapis.com/maps/api/geocode/json",
                params={
                    "address": test_address,
                    "key": GOOGLE_API_KEY
                }
            )
            
            execution_time = (datetime.now() - start_time).total_seconds() * 1000
            data = response.json()
            
            if data.get("status") == "OK":
                result = data["results"][0]
                return TestResult(
                    test_name="Geocoding API - Harrisonburg Test",
                    success=True,
                    response_data={
                        "input_address": test_address,
                        "formatted_address": result["formatted_address"],
                        "location": result["geometry"]["location"],
                        "place_id": result["place_id"]
                    },
                    execution_time_ms=execution_time,
                    timestamp=datetime.now().isoformat()
                )
            else:
                return TestResult(
                    test_name="Geocoding API - Harrisonburg Test",
                    success=False,
                    error_message=f"API Error: {data.get('status')} - {data.get('error_message', 'Unknown error')}",
                    execution_time_ms=execution_time,
                    timestamp=datetime.now().isoformat()
                )
                
    except Exception as e:
        execution_time = (datetime.now() - start_time).total_seconds() * 1000
        return TestResult(
            test_name="Geocoding API - Harrisonburg Test",
            success=False,
            error_message=f"Request failed: {str(e)}",
            execution_time_ms=execution_time,
            timestamp=datetime.now().isoformat()
        )

@router.get("/distance-matrix")
async def test_distance_matrix():
    """Test Distance Matrix API with Harrisonburg area locations"""
    if not GOOGLE_API_KEY:
        raise HTTPException(status_code=500, detail="Google API key not configured")
    
    start_time = datetime.now()
    
    # Test with Harrisonburg area locations
    origins = "James Madison University, Harrisonburg, VA"
    destinations = "Downtown Harrisonburg, VA|Massanutten Resort, VA|Bridgewater College, VA"
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://maps.googleapis.com/maps/api/distancematrix/json",
                params={
                    "origins": origins,
                    "destinations": destinations,
                    "mode": "driving",
                    "units": "imperial",  # Miles for US locations
                    "key": GOOGLE_API_KEY
                }
            )
            
            execution_time = (datetime.now() - start_time).total_seconds() * 1000
            data = response.json()
            
            if data.get("status") == "OK":
                return TestResult(
                    test_name="Distance Matrix API - Harrisonburg Area",
                    success=True,
                    response_data={
                        "origin": data["origin_addresses"][0],
                        "destinations": data["destination_addresses"],
                        "distances_and_times": data["rows"][0]["elements"]
                    },
                    execution_time_ms=execution_time,
                    timestamp=datetime.now().isoformat()
                )
            else:
                return TestResult(
                    test_name="Distance Matrix API - Harrisonburg Area",
                    success=False,
                    error_message=f"API Error: {data.get('status')} - {data.get('error_message', 'Unknown error')}",
                    execution_time_ms=execution_time,
                    timestamp=datetime.now().isoformat()
                )
                
    except Exception as e:
        execution_time = (datetime.now() - start_time).total_seconds() * 1000
        return TestResult(
            test_name="Distance Matrix API - Harrisonburg Area",
            success=False,
            error_message=f"Request failed: {str(e)}",
            execution_time_ms=execution_time,
            timestamp=datetime.now().isoformat()
        )

@router.get("/places")
async def test_places_api():
    """Test Places API with Harrisonburg area search"""
    if not GOOGLE_API_KEY:
        raise HTTPException(status_code=500, detail="Google API key not configured")
    
    start_time = datetime.now()
    test_query = "restaurants in Harrisonburg VA"
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://maps.googleapis.com/maps/api/place/textsearch/json",
                params={
                    "query": test_query,
                    "key": GOOGLE_API_KEY
                }
            )
            
            execution_time = (datetime.now() - start_time).total_seconds() * 1000
            data = response.json()
            
            if data.get("status") == "OK":
                # Return first 3 results for brevity
                results = data["results"][:3]
                simplified_results = []
                for place in results:
                    simplified_results.append({
                        "name": place.get("name"),
                        "address": place.get("formatted_address"),
                        "rating": place.get("rating"),
                        "place_id": place.get("place_id"),
                        "location": place.get("geometry", {}).get("location")
                    })
                
                return TestResult(
                    test_name="Places API - Harrisonburg Restaurants",
                    success=True,
                    response_data={
                        "query": test_query,
                        "total_results": len(data["results"]),
                        "sample_results": simplified_results
                    },
                    execution_time_ms=execution_time,
                    timestamp=datetime.now().isoformat()
                )
            else:
                return TestResult(
                    test_name="Places API - Harrisonburg Restaurants",
                    success=False,
                    error_message=f"API Error: {data.get('status')} - {data.get('error_message', 'Unknown error')}",
                    execution_time_ms=execution_time,
                    timestamp=datetime.now().isoformat()
                )
                
    except Exception as e:
        execution_time = (datetime.now() - start_time).total_seconds() * 1000
        return TestResult(
            test_name="Places API - Harrisonburg Restaurants",
            success=False,
            error_message=f"Request failed: {str(e)}",
            execution_time_ms=execution_time,
            timestamp=datetime.now().isoformat()
        )

@router.post("/harrisonburg-locations")
async def test_harrisonburg_batch():
    """Test multiple Harrisonburg locations for TSP planning"""
    if not GOOGLE_API_KEY:
        raise HTTPException(status_code=500, detail="Google API key not configured")
    
    start_time = datetime.now()
    
    # Common Harrisonburg locations for testing
    test_locations = [
        "James Madison University, Harrisonburg, VA",
        "Downtown Harrisonburg, VA",
        "Valley Mall, Harrisonburg, VA",
        "Harrisonburg High School, VA",
        "Rockingham Memorial Hospital, Harrisonburg, VA"
    ]
    
    try:
        geocoded_locations = []
        
        async with httpx.AsyncClient() as client:
            for address in test_locations:
                response = await client.get(
                    "https://maps.googleapis.com/maps/api/geocode/json",
                    params={
                        "address": address,
                        "key": GOOGLE_API_KEY
                    }
                )
                
                data = response.json()
                if data.get("status") == "OK":
                    result = data["results"][0]
                    geocoded_locations.append({
                        "input_address": address,
                        "formatted_address": result["formatted_address"],
                        "location": result["geometry"]["location"],
                        "place_id": result["place_id"]
                    })
                else:
                    geocoded_locations.append({
                        "input_address": address,
                        "error": f"{data.get('status')} - {data.get('error_message', 'Unknown error')}"
                    })
        
        execution_time = (datetime.now() - start_time).total_seconds() * 1000
        
        return TestResult(
            test_name="Batch Geocoding - Harrisonburg Locations",
            success=True,
            response_data={
                "total_locations": len(test_locations),
                "successfully_geocoded": len([loc for loc in geocoded_locations if "location" in loc]),
                "locations": geocoded_locations
            },
            execution_time_ms=execution_time,
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        execution_time = (datetime.now() - start_time).total_seconds() * 1000
        return TestResult(
            test_name="Batch Geocoding - Harrisonburg Locations",
            success=False,
            error_message=f"Request failed: {str(e)}",
            execution_time_ms=execution_time,
            timestamp=datetime.now().isoformat()
        )

@router.get("/full-test")
async def run_full_harrisonburg_test():
    """Run comprehensive test of all Google APIs with Harrisonburg data"""
    if not GOOGLE_API_KEY:
        raise HTTPException(status_code=500, detail="Google API key not configured")
    
    start_time = datetime.now()
    test_results = []
    
    # Test 1: Geocoding
    try:
        geocoding_result = await test_geocoding()
        test_results.append(geocoding_result.dict())
    except Exception as e:
        test_results.append({
            "test_name": "Geocoding API - Harrisonburg Test",
            "success": False,
            "error_message": str(e),
            "execution_time_ms": 0,
            "timestamp": datetime.now().isoformat()
        })
    
    # Test 2: Distance Matrix
    try:
        distance_result = await test_distance_matrix()
        test_results.append(distance_result.dict())
    except Exception as e:
        test_results.append({
            "test_name": "Distance Matrix API - Harrisonburg Area",
            "success": False,
            "error_message": str(e),
            "execution_time_ms": 0,
            "timestamp": datetime.now().isoformat()
        })
    
    # Test 3: Places API
    try:
        places_result = await test_places_api()
        test_results.append(places_result.dict())
    except Exception as e:
        test_results.append({
            "test_name": "Places API - Harrisonburg Restaurants",
            "success": False,
            "error_message": str(e),
            "execution_time_ms": 0,
            "timestamp": datetime.now().isoformat()
        })
    
    total_execution_time = (datetime.now() - start_time).total_seconds() * 1000
    successful_tests = sum(1 for result in test_results if result["success"])
    
    return {
        "project": "Harrisonburg Explorer",
        "test_summary": {
            "total_tests": len(test_results),
            "successful_tests": successful_tests,
            "failed_tests": len(test_results) - successful_tests,
            "success_rate": f"{(successful_tests / len(test_results) * 100):.1f}%",
            "total_execution_time_ms": total_execution_time
        },
        "individual_results": test_results,
        "timestamp": datetime.now().isoformat(),
        "next_steps": "If all tests pass, you're ready to build the TSP solver!"
    }