from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from app.schemas.user import UserResponse
from app.schemas.prediction import PredictionHistoryResponse
from app.schemas.feedback import FeedbackResponse

class AdminDashboardMetrics(BaseModel):
    total_users: int
    total_predictions: int
    total_feedbacks: int

class FeedbackWithPredictionResponse(FeedbackResponse):
    prediction: PredictionHistoryResponse

    class Config:
        from_attributes = True

class AdminFeedbackListResponse(BaseModel):
    items: List[FeedbackWithPredictionResponse]
    total: int
