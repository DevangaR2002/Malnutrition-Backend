import requests
import json

BASE_URL = "http://localhost:8000"

print("=== Test 1: Health Check ===")
response = requests.get(f"{BASE_URL}/")
print(f"Status: {response.status_code}")
print(f"Response: {response.json()}")

print("\n=== Test 2: High Risk Prediction ===")
high_risk_data = {
    "age_months": 24,
    "gender": "Male",
    "mother_education": "No education",
    "household_wealth_index": "Low",
    "height_cm": 70.0,
    "weight_kg": 8.5,
    "has_diarrhea": True,
    "has_malaria": True,
    "has_tb": False
}

response = requests.post(f"{BASE_URL}/api/predictions/predict", json=high_risk_data)
print(f"Status: {response.status_code}")

print(f"Response: {json.dumps(response.json(), indent=2)}")

print("\n=== Test 3: Low Risk Prediction ===")
low_risk_data = {
    "age_months": 36,
    "gender": "Female",
    "mother_education": "Secondary",
    "household_wealth_index": "High",
    "height_cm": 95.0,
    "weight_kg": 14.0,
    "has_diarrhea": False,
    "has_malaria": False,
    "has_tb": False
}

response = requests.post(f"{BASE_URL}/api/predictions/predict", json=low_risk_data)
print(f"Status: {response.status_code}")
print(f"Response: {json.dumps(response.json(), indent=2)}")

print("\n✅ Debug tests completed!")