import json
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def get_auth_token():
    import uuid
    unique_user = f"testuser_tier_{uuid.uuid4().hex[:6]}"
    
    client.post(
        "/auth/register",
        json={"username": unique_user, "email": f"{unique_user}@example.com", "password": "testpassword123"}
    )
    
    response = client.post(
        "/auth/login",
        data={"username": unique_user, "password": "testpassword123"}
    )
    return response.json()["access_token"]

token = get_auth_token()
headers = {"Authorization": f"Bearer {token}"}

print("Testing 3-Tier Risk Classification...")

def submit_prediction(name, payload):
    print(f"\n--- Testing Scenario: {name} ---")
    response = client.post("/api/predictions/predict", json=payload, headers=headers)
    if response.status_code == 201:
        data = response.json()
        print(f"Assigned Risk Level : {data.get('risk_level')}")
        print(f"Risk Probability    : {data.get('risk_probability')}")
        print(f"Confidence          : {data.get('confidence')}")
        return data
    else:
        print("Failure!", response.status_code, response.json())
        return None

submit_prediction("Low Risk", {
    "age_months": 24,
    "gender": "Male",
    "mother_education": "Secondary",
    "household_wealth_index": "Middle",
    "height_cm": 88.0,
    "weight_kg": 12.5,
    "has_diarrhea": False,
    "has_malaria": False,
    "has_tb": False
})

submit_prediction("Medium Risk", {
    "age_months": 12,
    "gender": "Female",
    "mother_education": "Primary",
    "household_wealth_index": "Middle",
    "height_cm": 75.0,  
    "weight_kg": 9.2,   
    "has_diarrhea": False, 
    "has_malaria": False,
    "has_tb": False
})

submit_prediction("High Risk", {
    "age_months": 36,
    "gender": "Male",
    "mother_education": "No education",
    "household_wealth_index": "Low",
    "height_cm": 80.0, 
    "weight_kg": 9.0,  
    "has_diarrhea": True,
    "has_malaria": True,
    "has_tb": True
})

print("\nTests completed.")
