from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List
import csv
import io

from app.database import get_db
from app.models.prediction import Prediction
from app.schemas.prediction import (
    ChildDataInput,
    PredictionResponse,
    PredictionHistoryResponse
)
from app.services.ml_service import ml_service
from app.services.auth import get_current_active_user
from app.services.preprocessing import preprocessing_service
from app.models.user import User
from app.models.feedback import PredictionFeedback
from app.schemas.feedback import FeedbackCreate, FeedbackResponse

router = APIRouter(prefix="/api/predictions", tags=["Predictions"])


@router.post("/predict", response_model=PredictionResponse, status_code=status.HTTP_201_CREATED)
async def create_prediction(
    data: ChildDataInput,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Create a new malnutrition risk prediction for a child.
    
    - **age_months**: Age of the child in months (0-60)
    - **gender**: Male or Female
    - **mother_education**: No education, Primary, Secondary, or Higher
    - **household_wealth_index**: Low, Middle, or High
    - **height_cm**: Height in centimeters
    - **weight_kg**: Weight in kilograms
    - **has_diarrhea**: Whether the child has diarrhea
    - **has_malaria**: Whether the child has malaria
    - **has_tb**: Whether the child has tuberculosis
    """
    
    try:
        
        raw_data = data.model_dump(exclude_unset=True)
    
        input_data = preprocessing_service.process(raw_data)
        
        result = ml_service.predict(input_data)
        
        db_prediction = Prediction(
            age_months=input_data['age_months'],
            gender=input_data['gender'],
            mother_education=input_data['mother_education'],
            household_wealth_index=input_data['household_wealth_index'],
            height_cm=input_data['height_cm'],
            weight_kg=input_data['weight_kg'],
            has_diarrhea=input_data['has_diarrhea'],
            has_malaria=input_data['has_malaria'],
            has_tb=input_data['has_tb'],
            prediction=result['prediction'],
            risk_probability=result['risk_probability'],
            risk_level=result['risk_level'],
            user_id=current_user.id
        )
        
        db.add(db_prediction)
        db.commit()
        db.refresh(db_prediction)
        
        # Prepare response
        response = PredictionResponse(
            id=db_prediction.id,
            prediction=result['prediction'],
            risk_level=result['risk_level'],
            risk_probability=result['risk_probability'],
            confidence=result['confidence'],
            recommendations=result['recommendations'],
            xai=result.get("xai"),
            xai_text= result.get("xai_text"),
            input_summary={
                'age_months': input_data['age_months'],
                'gender': input_data['gender'],
                'height_cm': input_data['height_cm'],
                'weight_kg': input_data['weight_kg']
            },
            created_at=db_prediction.created_at
        )
        
        return response
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Prediction failed: {str(e)}"
        )


@router.get("/history", response_model=List[PredictionHistoryResponse])
async def get_prediction_history(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
   
    
    query = db.query(Prediction)
    
    if not current_user.is_admin:
        query = query.filter(Prediction.user_id == current_user.id)
        
    predictions = query.order_by(Prediction.created_at.desc())\
        .offset(skip)\
        .limit(limit)\
        .all()
    
    return predictions


@router.get("/{prediction_id}", response_model=PredictionResponse)
async def get_prediction(
    prediction_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
   
    
    query = db.query(Prediction).filter(Prediction.id == prediction_id)
    if not current_user.is_admin:
        query = query.filter(Prediction.user_id == current_user.id)
    
    prediction = query.first()
    
    if not prediction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Prediction with ID {prediction_id} not found"
        )
        
    input_data = {
        'age_months': prediction.age_months,
        'gender': prediction.gender,
        'mother_education': prediction.mother_education,
        'household_wealth_index': prediction.household_wealth_index,
        'height_cm': prediction.height_cm,
        'weight_kg': prediction.weight_kg,
        'has_diarrhea': prediction.has_diarrhea,
        'has_malaria': prediction.has_malaria,
        'has_tb': prediction.has_tb
    }
    
    processed_data = preprocessing_service.process(input_data)
    result = ml_service.predict(processed_data)
    
    return PredictionResponse(
        id=prediction.id,
        prediction=prediction.prediction,
        risk_level=prediction.risk_level,
        risk_probability=prediction.risk_probability,
        confidence=result['confidence'],
        recommendations=result['recommendations'],
        xai=result.get("xai"),
        xai_text=result.get("xai_text"),
        input_summary=prediction.input_summary,
        created_at=prediction.created_at
    )


@router.delete("/{prediction_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_prediction(
    prediction_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    
    
    query = db.query(Prediction).filter(Prediction.id == prediction_id)
    if not current_user.is_admin:
        query = query.filter(Prediction.user_id == current_user.id)
    
    prediction = query.first()
    
    if not prediction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Prediction with ID {prediction_id} not found"
        )
    
    db.delete(prediction)
    db.commit()
    
    return None


@router.post("/{prediction_id}/feedback", response_model=FeedbackResponse, status_code=status.HTTP_201_CREATED)
async def submit_feedback(
    prediction_id: int,
    feedback_data: FeedbackCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    
    
    query = db.query(Prediction).filter(Prediction.id == prediction_id)
    if not current_user.is_admin:
        query = query.filter(Prediction.user_id == current_user.id)
        
    prediction = query.first()
    if not prediction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Prediction with ID {prediction_id} not found"
        )
        
   
    existing_feedback = db.query(PredictionFeedback).filter(PredictionFeedback.prediction_id == prediction_id).first()
    if existing_feedback:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Feedback for this prediction already exists"
        )
        
    db_feedback = PredictionFeedback(
        prediction_id=prediction_id,
        is_correct=feedback_data.is_correct,
        actual_risk_level=feedback_data.actual_risk_level,
        comments=feedback_data.comments
    )
    
    db.add(db_feedback)
    db.commit()
    db.refresh(db_feedback)
    
    return db_feedback


@router.get("/export/dataset", response_class=StreamingResponse)
async def export_dataset(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
   
     
    predictions = db.query(Prediction).all()
    stream = io.StringIO()
    fieldnames = [
        "prediction_id", 
        "created_at",
        "age_months", 
        "gender", 
        "mother_education", 
        "household_wealth_index",
        "height_cm", 
        "weight_kg", 
        "has_diarrhea", 
        "has_malaria", 
        "has_tb",
        "prediction_float",
        "risk_probability",
        "predicted_risk_level",
        "clinician_has_feedback",
        "clinician_is_correct",
        "clinician_actual_risk_level",
        "clinician_comments"
    ]
    
    writer = csv.DictWriter(stream, fieldnames=fieldnames)
    writer.writeheader()
    
    for pred in predictions:
        row = {
            "prediction_id": pred.id,
            "created_at": pred.created_at.isoformat() if pred.created_at else "",
            "age_months": pred.age_months,
            "gender": pred.gender,
            "mother_education": pred.mother_education,
            "household_wealth_index": pred.household_wealth_index,
            "height_cm": pred.height_cm,
            "weight_kg": pred.weight_kg,
            "has_diarrhea": pred.has_diarrhea,
            "has_malaria": pred.has_malaria,
            "has_tb": pred.has_tb,
            "prediction_float": pred.prediction,
            "risk_probability": round(pred.risk_probability, 4) if pred.risk_probability else None,
            "predicted_risk_level": pred.risk_level,
            "clinician_has_feedback": False,
            "clinician_is_correct": "",
            "clinician_actual_risk_level": "",
            "clinician_comments": ""
        }
        
        if hasattr(pred, 'feedback') and pred.feedback:

            feedback = pred.feedback[0] if isinstance(pred.feedback, list) and len(pred.feedback) > 0 else pred.feedback
            
            if feedback and not isinstance(feedback, list):
                row["clinician_has_feedback"] = True
                row["clinician_is_correct"] = feedback.is_correct
                row["clinician_actual_risk_level"] = getattr(feedback, "actual_risk_level", "")
                
                row["clinician_comments"] = getattr(feedback, "comments", "")
                
        writer.writerow(row)
        
    stream.seek(0)
    
    return StreamingResponse(
        iter([stream.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=malnutriaid_research_export.csv"}
    )
