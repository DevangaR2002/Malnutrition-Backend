from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class GenderEnum(str, Enum):
    male = "Male"
    female = "Female"


class EducationEnum(str, Enum):
    no_education = "No education"
    primary = "Primary"
    secondary = "Secondary"
    higher = "Higher"


class WealthIndexEnum(str, Enum):
    low = "Low"
    middle = "Middle"
    high = "High"


class ChildDataInput(BaseModel):
    """Input schema for child data"""
    
    age_months: Optional[int] = Field(None, ge=0, le=59, description="Age in months (0-59)")
    gender: Optional[str] = Field(None, description="Gender of the child")
    mother_education: Optional[str] = Field(None, description="Mother's education level")
    household_wealth_index: Optional[str] = Field(None, description="Household wealth index")
    height_cm: Optional[float] = Field(None, description="Height in centimeters")
    weight_kg: Optional[float] = Field(None, description="Weight in kilograms")
    has_diarrhea: Optional[bool] = Field(default=False, description="Has diarrhea")
    has_malaria: Optional[bool] = Field(default=False, description="Has malaria")
    has_tb: Optional[bool] = Field(default=False, description="Has tuberculosis")
    
    class Config:
        json_schema_extra = {
            "example": {
                "age_months": 24,
                "gender": "Male",
                "mother_education": "Primary",
                "household_wealth_index": "Low",
                "height_cm": 85.5,
                "weight_kg": 11.2,
                "has_diarrhea": False,
                "has_malaria": False,
                "has_tb": False
            }
        }


class RecommendationItem(BaseModel):
    """Schema for individual recommendation"""
    category: str
    recommendation: str
    source: str

class XAIFactor(BaseModel):
    feature: str
    impact: float

class XAIResponse(BaseModel):
    top_factors: List[XAIFactor]


class PredictionResponse(BaseModel):
    """Response schema for prediction results"""
    
    id: int
    prediction: int
    risk_level: str
    risk_probability: float
    confidence: str
    recommendations: List[RecommendationItem]
    input_summary: dict

    xai: Optional[XAIResponse] = None
    xai_text: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class PredictionHistoryResponse(BaseModel):
    """Response schema for prediction history"""
    
    id: int
    age_months: int
    gender: str
    risk_level: str
    risk_probability: float
    input_summary: dict
    created_at: datetime
    
    class Config:
        from_attributes = True