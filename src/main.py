"""
CMA Analysis Tool - Main Entry Point
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import router as api_router
from api.auth_routes import router as auth_router
from core.config import settings
from data.database import create_tables
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_app() -> FastAPI:
    """Create FastAPI application"""
    app = FastAPI(
        title="CMA Analysis API",
        description="Comparative Market Analysis Tool with Authentication",
        version="1.0.0"
    )
    
    # Add CORS middleware - THIS IS THE FIX!
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Include API routes
    app.include_router(api_router, prefix="/api/v1")
    app.include_router(auth_router, prefix="/api/v1/auth")
    
    return app

app = create_app()

@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    logger.info("Starting up CMA Analysis Tool...")
    create_tables()
    logger.info("Database initialized successfully")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
