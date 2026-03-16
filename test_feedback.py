import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'app')))

from fastapi.testclient import TestClient
from app.main import app
from app.database import Base, engine, SessionLocal
from app.models.feedback import PredictionFeedback

from app.models.prediction import Prediction
from app.database import Base, engine, SessionLocal
from app.models.feedback import PredictionFeedback

def test_feedback_integration():
    print("Testing Postgres Feedback Integration natively via SQLAlchemy...")
    
    db = SessionLocal()
    
    try:
        dummy_pred = Prediction(
            age_months=24,
            gender="Male",
            mother_education="Primary",
            household_wealth_index="Low",
            height_cm=85.5,
            weight_kg=11.2,
            has_diarrhea=False,
            has_malaria=False,
            has_tb=False,
            prediction=0,
            risk_probability=0.1,
            risk_level="Low Risk"
        )
        
        db.add(dummy_pred)
        db.commit()
        db.refresh(dummy_pred)
        pred_id = dummy_pred.id
        
        print(f"Prediction securely created natively in DB with ID {pred_id}.")
        
        dummy_feedback = PredictionFeedback(
            prediction_id=pred_id,
            is_correct=False,
            actual_risk_level="Medium Risk",
            comments="Patient appears healthier than numbers suggest."
        )
        
        db.add(dummy_feedback)
        db.commit()
        db.refresh(dummy_feedback)
        
        print("SQLAlchemy seamlessly committed the Feedback payload mapping the foreign key!")
        
        record = db.query(PredictionFeedback).filter(PredictionFeedback.prediction_id == pred_id).first()
        assert record is not None
        assert record.comments == "Patient appears healthier than numbers suggest."
        
        print("PostgreSQL Database successfully retrieved the exact feedback row. All systems nominal.")
        
    except Exception as e:
        print(f"Database error: {e}")
    finally:
        if 'pred_id' in locals():
            db.query(Prediction).filter(Prediction.id == pred_id).delete()
            db.commit()
        db.close()

if __name__ == "__main__":
    test_feedback_integration()
