# backend/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import json

# Create FastAPI instance
app = FastAPI(title="Your App API", version="1.0.0")

# Add CORS middleware to allow frontend to communicate with backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Sample data
sample_data = {
    "message": "Hello from FastAPI!",
    "status": "success",
    "timestamp": datetime.now().isoformat(),
    "data": [
        {"id": 1, "name": "John Doe", "email": "john@example.com"},
        {"id": 2, "name": "Jane Smith", "email": "jane@example.com"},
        {"id": 3, "name": "Bob Johnson", "email": "bob@example.com"}
    ],
    "meta": {
        "total_users": 3,
        "version": "1.0.0",
        "environment": "development"
    }
}

@app.get("/")
async def root():
    """Root endpoint - API health check"""
    return {"message": "FastAPI is running!", "status": "healthy"}

@app.get("/test")
async def get_test_data():
    """Test endpoint serving sample JSON data"""
    return sample_data

@app.get("/test/{item_id}")
async def get_test_item(item_id: int):
    """Get a specific item from test data"""
    users = sample_data["data"]
    user = next((user for user in users if user["id"] == item_id), None)
    
    if user:
        return {
            "message": f"User {item_id} found",
            "status": "success",
            "data": user
        }
    else:
        return {
            "message": f"User {item_id} not found",
            "status": "error",
            "data": None
        }

@app.post("/test")
async def create_test_item(item: dict):
    """Create a new test item (example POST endpoint)"""
    return {
        "message": "Item created successfully",
        "status": "success",
        "received_data": item,
        "timestamp": datetime.now().isoformat()
    }

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "backend-api"
    }