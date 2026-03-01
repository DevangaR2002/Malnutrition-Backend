from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Prediction(Base):
    """SQLAlchemy model for storing predictions"""
    
    __tablename__ = "predictions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True) 
    
    
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
    
    user = relationship("User", back_populates="predictions")
    
    @property
    def input_summary(self):
        return {
            "age_months": self.age_months,
            "gender": self.gender,
            "height_cm": self.height_cm,
            "weight_kg": self.weight_kg
        }
    
    def __repr__(self):
        return f"<Prediction(id={self.id}, risk_level={self.risk_level})>"