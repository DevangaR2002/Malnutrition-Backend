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
    
    age_months: int = Field(..., ge=0, le=60, description="Age in months (0-60)")
    gender: GenderEnum = Field(..., description="Gender of the child")
    mother_education: EducationEnum = Field(..., description="Mother's education level")
    household_wealth_index: WealthIndexEnum = Field(..., description="Household wealth index")
    height_cm: float = Field(..., ge=30, le=150, description="Height in centimeters")
    weight_kg: float = Field(..., ge=1, le=40, description="Weight in kilograms")
    has_diarrhea: bool = Field(default=False, description="Has diarrhea")
    has_malaria: bool = Field(default=False, description="Has malaria")
    has_tb: bool = Field(default=False, description="Has tuberculosis")
    
    @validator('height_cm')
    def validate_height(cls, v, values):
        """Validate height based on age"""
        age = values.get('age_months', 0)
        if age <= 6 and v > 80:
            raise ValueError(f"Height {v}cm is too high for a {age}-month-old child")
        if age <= 12 and v > 100:
            raise ValueError(f"Height {v}cm is too high for a {age}-month-old child")
        return v
    
    @validator('weight_kg')
    def validate_weight(cls, v, values):
        """Validate weight based on age"""
        age = values.get('age_months', 0)
        if age <= 6 and v > 12:
            raise ValueError(f"Weight {v}kg is too high for a {age}-month-old child")
        if age <= 12 and v > 15:
            raise ValueError(f"Weight {v}kg is too high for a {age}-month-old child")
        return v
    
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


class PredictionResponse(BaseModel):
    """Response schema for prediction results"""
    
    id: int
    prediction: int
    risk_level: str
    risk_probability: float
    confidence: str
    recommendations: List[RecommendationItem]
    input_summary: dict
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
    created_at: datetime
    
    class Config:
        from_attributes = True