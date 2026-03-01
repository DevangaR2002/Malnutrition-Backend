from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class PredictionFeedback(Base):

    
    __tablename__ = "predictions_feedback"
    
    id = Column(Integer, primary_key=True, index=True)
    prediction_id = Column(Integer, ForeignKey("predictions.id", ondelete="CASCADE"), nullable=False, unique=True)
    
    is_correct = Column(Boolean, nullable=False)
    actual_risk_level = Column(String(50), nullable=True)
    comments = Column(Text, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    prediction = relationship("Prediction", backref="feedback")
    
    def __repr__(self):
        return f"<PredictionFeedback(id={self.id}, prediction_id={self.prediction_id}, is_correct={self.is_correct})>"
