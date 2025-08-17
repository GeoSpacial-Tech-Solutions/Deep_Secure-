from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import os

from app.api import video, auth
from app.database import create_tables, engine
from app.models import Base

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("Starting DeepSecure ID system...")
    
    # Create database tables
    try:
        create_tables()
        print("Database tables created successfully")
    except Exception as e:
        print(f"Warning: Database initialization failed: {e}")
    
    # Create uploads directory
    os.makedirs("./uploads", exist_ok=True)
    os.makedirs("./models", exist_ok=True)
    
    yield
    
    # Shutdown
    print("Shutting down DeepSecure ID system...")

app = FastAPI(
    title="DeepSecure ID: AI-Driven Biometric Verification and Deepfake Detection System",
    description="End-to-end modular, production-ready deepfake and geospatial authenticity detection system",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(auth.router, prefix="/api")
app.include_router(video.router, prefix="/api")

# Health check endpoint
@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "DeepSecure ID",
        "version": "1.0.0"
    }

# Root endpoint
@app.get("/")
def root():
    return {
        "message": "DeepSecure ID API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }

# API info endpoint
@app.get("/api/info")
def api_info():
    return {
        "name": "DeepSecure ID API",
        "version": "1.0.0",
        "description": "AI-Driven Biometric Verification and Deepfake Detection System",
        "features": [
            "Deepfake Detection",
            "Geospatial Verification",
            "User Authentication",
            "Video Analysis",
            "Real-time Processing"
        ],
        "endpoints": {
            "authentication": "/api/auth",
            "video_analysis": "/api/video",
            "documentation": "/docs"
        }
    } 