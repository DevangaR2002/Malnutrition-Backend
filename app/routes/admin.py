from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.user import User
from app.models.prediction import Prediction
from app.models.feedback import PredictionFeedback
from app.services.auth import get_current_active_user, get_current_admin_user

from app.schemas.user import UserResponse
from app.schemas.admin import AdminDashboardMetrics, FeedbackWithPredictionResponse, AdminFeedbackListResponse

router = APIRouter(prefix="/api/admin", tags=["Admin System"])

@router.get("/users", response_model=List[UserResponse])
async def get_all_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    
    accounts = db.query(User).all()
    return accounts

@router.put("/users/{user_id}/toggle-status")
async def toggle_user_status(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Toggle a user's active status (revoke/grant access)"""
    user_to_toggle = db.query(User).filter(User.id == user_id).first()
    
    if not user_to_toggle:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        
    # Prevent admins from disabling themselves
    if user_to_toggle.id == current_user.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You cannot revoke your own access.")
        
    user_to_toggle.is_active = not user_to_toggle.is_active
    db.commit()
    
    status_msg = "restored" if user_to_toggle.is_active else "revoked"
    return {"message": f"Successfully {status_msg} access for user {user_to_toggle.username}", "is_active": user_to_toggle.is_active}

@router.get("/metrics", response_model=AdminDashboardMetrics)
async def get_system_metrics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Compute top-level system activity metrics"""
    user_count = db.query(User).count()
    pred_count = db.query(Prediction).count()
    feedback_count = db.query(PredictionFeedback).count()
    
    return {
        "total_users": user_count,
        "total_predictions": pred_count,
        "total_feedbacks": feedback_count
    }

@router.get("/feedback", response_model=List[FeedbackWithPredictionResponse])
async def get_system_feedback(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
   
    feedbacks = db.query(PredictionFeedback).order_by(PredictionFeedback.created_at.desc()).offset(skip).limit(limit).all()
    
    return feedbacks
