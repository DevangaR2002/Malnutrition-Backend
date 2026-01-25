from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime
from sqlalchemy.sql import func
from app.database import Base


class Prediction(Base):
    """SQLAlchemy model for storing predictions"""
    
    __tablename__ = "predictions"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Child Information
    age_months = Column(Integer, nullable=False)
    gender = Column(String(10), nullable=False)
    
    # Socioeconomic Factors
    mother_education = Column(String(50), nullable=False)
    household_wealth_index = Column(String(20), nullable=False)
    
    # Anthropometric Measurements
    height_cm = Column(Float, nullable=False)
    weight_kg = Column(Float, nullable=False)
    
    # Health Conditions
    has_diarrhea = Column(Boolean, default=False)
    has_malaria = Column(Boolean, default=False)
    has_tb = Column(Boolean, default=False)
    
    # Prediction Results
    prediction = Column(Integer, nullable=False) 
    risk_probability = Column(Float, nullable=False)
    risk_level = Column(String(20), nullable=False) 
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<Prediction(id={self.id}, risk_level={self.risk_level})>"