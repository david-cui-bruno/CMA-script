"""
Configuration settings for CMA Analysis Tool
"""
from pydantic_settings import BaseSettings
from typing import Optional
import secrets
import os

class Settings(BaseSettings):
    # Database - Use your actual username instead of postgres
    database_url: str = f"postgresql://{os.getenv('USER', 'davidcui824')}@localhost/cma_db"
    redis_url: str = "redis://localhost:6379"
    
    # Security
    secret_key: str = secrets.token_urlsafe(32)  # Generate random secret key
    
    # API Keys
    mls_api_key: Optional[str] = None
    google_maps_api_key: Optional[str] = None
    
    # Application
    debug: bool = True
    log_level: str = "INFO"
    max_comparables: int = 6
    default_search_radius: float = 1.0
    
    # Analysis Parameters
    max_days_old: int = 180  # Only use sales within 6 months
    min_similarity_score: float = 0.6
    
    # API Settings
    api_title: str = "CMA Analysis API"
    api_version: str = "1.0.0"
    
    # CORS origins
    cors_origins: list = ["http://localhost:3000", "http://127.0.0.1:3000"]
    
    class Config:
        env_file = ".env"

settings = Settings()
