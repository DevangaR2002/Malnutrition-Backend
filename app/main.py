from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.config import get_settings
from app.database import engine, Base
from app.routes.predictions import router as predictions_router

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle events for the application"""
    print("Starting up...")
    
    # Create database tables
    Base.metadata.create_all(bind=engine)
    print("Database tables created")
    
    yield
    
    print("Shutting down...")


app = FastAPI(
    title=settings.app_name,
    description="""
    ## Malnutrition Risk Prediction API
    
    This API predicts malnutrition risk in children based on various factors including:
    - Demographic information (age, gender)
    - Socioeconomic factors (mother's education, household wealth)
    - Anthropometric measurements (height, weight)
    - Health conditions (diarrhea, malaria, TB)
    
    The prediction model uses a **Hybrid Boosting Ensemble** combining XGBoost, LightGBM, 
    and CatBoost for maximum accuracy.
    
    ### Data Quality Note
    The training data contained some inconsistencies such as records labeled "Normal" 
    but having multiple risk indicators [1].
    """,
    version=settings.app_version,
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(predictions_router)


@app.get("/", tags=["Health"])
async def root():
    """Root endpoint - Health check"""
    return {
        "message": "Malnutrition Risk Prediction API",
        "status": "healthy",
        "version": settings.app_version
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "database": "connected",
        "model": "loaded"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug
    )