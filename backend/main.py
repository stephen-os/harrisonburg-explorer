# backend/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime

# Import routers
from routers import test_api

# Create FastAPI instance
app = FastAPI(
    title="Harrisonburg Explorer API", 
    version="1.0.0",
    description="Backend API for Harrisonburg Explorer - TSP route optimization"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(test_api.router, prefix="/api/test", tags=["Google API Testing"])

@app.get("/")
async def root():
    """Root endpoint - API health check"""
    return {
        "message": "Harrisonburg Explorer API is running!",
        "status": "healthy",
        "version": "1.0.0",
        "docs": "Visit /docs for API documentation"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "harrisonburg-explorer-api"
    }