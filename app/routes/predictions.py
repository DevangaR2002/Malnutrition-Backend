from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.prediction import Prediction
from app.schemas.prediction import (
    ChildDataInput,
    PredictionResponse,
    PredictionHistoryResponse
)
from app.services.ml_service import ml_service

router = APIRouter(prefix="/api/predictions", tags=["Predictions"])


@router.post("/predict", response_model=PredictionResponse, status_code=status.HTTP_201_CREATED)
async def create_prediction(
    data: ChildDataInput,
    db: Session = Depends(get_db)
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
        # Convert Pydantic model to dict
        input_data = {
            'age_months': data.age_months,
            'gender': data.gender.value,
            'mother_education': data.mother_education.value,
            'household_wealth_index': data.household_wealth_index.value,
            'height_cm': data.height_cm,
            'weight_kg': data.weight_kg,
            'has_diarrhea': data.has_diarrhea,
            'has_malaria': data.has_malaria,
            'has_tb': data.has_tb
        }
        
        # Make prediction using ML service
        result = ml_service.predict(input_data)
        
        # Save to database
        db_prediction = Prediction(
            age_months=data.age_months,
            gender=data.gender.value,
            mother_education=data.mother_education.value,
            household_wealth_index=data.household_wealth_index.value,
            height_cm=data.height_cm,
            weight_kg=data.weight_kg,
            has_diarrhea=data.has_diarrhea,
            has_malaria=data.has_malaria,
            has_tb=data.has_tb,
            prediction=result['prediction'],
            risk_probability=result['risk_probability'],
            risk_level=result['risk_level']
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
                'age_months': data.age_months,
                'gender': data.gender.value,
                'height_cm': data.height_cm,
                'weight_kg': data.weight_kg
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
    db: Session = Depends(get_db)
):
    """Get prediction history with pagination"""
    
    predictions = db.query(Prediction)\
        .order_by(Prediction.created_at.desc())\
        .offset(skip)\
        .limit(limit)\
        .all()
    
    return predictions


@router.get("/{prediction_id}", response_model=PredictionHistoryResponse)
async def get_prediction(
    prediction_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific prediction by ID"""
    
    prediction = db.query(Prediction).filter(Prediction.id == prediction_id).first()
    
    if not prediction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Prediction with ID {prediction_id} not found"
        )
    
    return prediction


@router.delete("/{prediction_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_prediction(
    prediction_id: int,
    db: Session = Depends(get_db)
):
    """Delete a prediction by ID"""
    
    prediction = db.query(Prediction).filter(Prediction.id == prediction_id).first()
    
    if not prediction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Prediction with ID {prediction_id} not found"
        )
    
    db.delete(prediction)
    db.commit()
    
    return None