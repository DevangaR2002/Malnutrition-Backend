from fastapi.testclient import TestClient
from app.main import app
from app.database import Base, engine


Base.metadata.create_all(bind=engine)

client = TestClient(app)

def test_auth_flow():
    username = "testdoc"
    email = "testdoc@example.com"
    password = "secretpassword"
    
    print("Testing Registration...")
    res = client.post("/auth/register", json={"username": username, "email": email, "password": password})
    if res.status_code == 201:
        print("Registration successful!")
    elif res.status_code == 400 and "already registered" in res.text:
        print("User already registered - proceeding to login test.")
    else:
        print(f"Registration failed: {res.status_code} {res.text}")
        return
        
   
    print("Testing Login...")
    res = client.post("/auth/login", data={"username": username, "password": password})
    if res.status_code == 200:
        token = res.json().get("access_token")
        print("Login successful! Token received.")
    else:
        print(f"Login failed: {res.status_code} {res.text}")
        return

    
    print("Testing Protected Route without token...")
    res = client.get("/api/predictions/history")
    if res.status_code == 401:
        print("Protected route blocked unauthorized access successfully.")
    else:
        print(f"Error: unauthorized access allowed: {res.status_code}")
        
   
    print("Testing Protected Route with token...")
    res = client.get("/api/predictions/history", headers={"Authorization": f"Bearer {token}"})
    if res.status_code == 200:
        print("Protected route accessed successfully with token.")
    else:
        print(f"Failed to access protected route with token: {res.status_code} {res.text}")

if __name__ == "__main__":
    test_auth_flow()
