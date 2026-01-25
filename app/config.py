from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    database_url: str = "postgresql://postgres:BBB_54321@localhost:5432/malnutrition_db"
    
    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    debug: bool = True
    
    # ML Model
    model_path: str = "ml_models/best_ensemble_model.pkl"
    scaler_path: str = "ml_models/scaler.pkl"
    
    app_name: str = "Malnutrition Risk Predictor"
    app_version: str = "1.0.0"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()