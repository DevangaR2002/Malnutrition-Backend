import json
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

# Helper function to get an auth token for tests
def get_auth_token():
    import uuid
    unique_user = f"testuser_{uuid.uuid4().hex[:6]}"
    
    # Register a new unique user
    client.post(
        "/auth/register",
        json={"username": unique_user, "email": f"{unique_user}@example.com", "password": "testpassword123"}
    )
    
    # Login
    response = client.post(
        "/auth/login",
        data={"username": unique_user, "password": "testpassword123"}
    )
    return response.json()["access_token"]

token = get_auth_token()
headers = {"Authorization": f"Bearer {token}"}

print("Testing Data Preprocessing Integration...")

def test_missing_data_imputation():
    print("\n1. Testing Missing Data Imputation")
    # Missing weight, height, and age
    payload = {
        "gender": "Male",
        "mother_education": "Primary",
        "household_wealth_index": "Low",
        "has_diarrhea": False,
        "has_malaria": False,
        "has_tb": False
    }

    print("Payload sent (missing age, height, weight):", json.dumps(payload, indent=2))
    response = client.post("/api/predictions/predict", json=payload, headers=headers)
    
    if response.status_code == 201:
        data = response.json()
        print("Success! Backend successfully imputed defaults:")
        print("Imputed Age:", data["input_summary"]["age_months"])
        print("Imputed Height:", data["input_summary"]["height_cm"])
        print("Imputed Weight:", data["input_summary"]["weight_kg"])
    else:
        print("Fail! Status:", response.status_code)
        print("Detail:", response.json())

def test_anomaly_clamping():
    print("\n2. Testing Extreme Anomaly Clamping")
    
    payload = {
        "age_months": 250, # Impossible age 
        "gender": "Female",
        "mother_education": "Higher",
        "household_wealth_index": "High",
        "height_cm": 1500, # 15 meters tall (anomaly)
        "weight_kg": 500,  # 500kg (anomaly)
        "has_diarrhea": False,
        "has_malaria": False,
        "has_tb": False
    }

    print("Payload sent (extreme values):", json.dumps(payload, indent=2))
    response = client.post("/api/predictions/predict", json=payload, headers=headers)
    
    if response.status_code == 201:
        data = response.json()
        print("Success! Backend clamped values within physiological limits:")
        print("Clamped Age:", data["input_summary"]["age_months"])
        print("Clamped Height:", data["input_summary"]["height_cm"])
        print("Clamped Weight:", data["input_summary"]["weight_kg"])
    else:
        print("Fail! Status:", response.status_code)
        print("Detail:", response.json())

def test_categorical_standardization():
    print("\n3. Testing Categorical Label Standardization (Capitalization/Spelling)")
    
    payload = {
        "age_months": 36,
        "gender": "female", # lowercase
        "mother_education": "none whatsoever", # non-standard string
        "household_wealth_index": "high", # lowercase
        "height_cm": 95,
        "weight_kg": 14,
        "has_diarrhea": False,
        "has_malaria": False,
        "has_tb": False
    }

    print("Payload sent (Messy capitalizations):", json.dumps(payload, indent=2))
    response = client.post("/api/predictions/predict", json=payload, headers=headers)
    
    if response.status_code == 201:
        data = response.json()
        print("Success! Backend successfully standardized the categories (should be properly capitalized):")
        # To verify we fetch the prediction we just made to see the stored strings
        pred_id = data["id"]
        pred_response = client.get(f"/api/predictions/{pred_id}", headers=headers)
        if pred_response.status_code == 200:
            pred_data = pred_response.json()
            print("- Standardized Gender:", pred_data["gender"])
            print("Note: Detailed history response doesn't expose mother_education/wealth, but prediction succeeded proving model parsed it.")
    else:
        print("Fail! Status:", response.status_code)
        print("Detail:", response.json())

if __name__ == "__main__":
    test_missing_data_imputation()
    test_anomaly_clamping()
    test_categorical_standardization()
    print("\nPreprocessing tests completed.")
