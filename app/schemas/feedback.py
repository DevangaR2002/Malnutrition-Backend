from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class FeedbackCreate(BaseModel):
    is_correct: bool = Field(..., description="Whether the doctor agreed with the AI prediction")
    actual_risk_level: Optional[str] = Field(None, description="The true risk level observed by the clinician")
    comments: Optional[str] = Field(None, description="Additional notes/justification from the clinician")


class FeedbackResponse(BaseModel):
    id: int
    prediction_id: int
    is_correct: bool
    actual_risk_level: Optional[str]
    comments: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True
