import os
import argparse
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from app.database import Base
from app.models.user import User

# Load environment variables
load_dotenv()

def create_admin(username: str):
    db_url = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/malnutrition_db")
    print(f"Connecting to database: {db_url}")
    
    engine = create_engine(db_url)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        user = db.query(User).filter(User.username == username).first()
        
        if not user:
            print(f"Error: User '{username}' not found in the database.")
            return
            
        if user.is_admin:
            print(f"User '{username}' is already an administrator!")
            return
            
        # Upgrade to admin
        user.is_admin = True
        db.commit()
        print(f"SUCCESS: User '{username}' has been upgraded to an Administrator!")
        
    except Exception as e:
        print(f"Failed to upgrade user: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Grant Administrator privileges to an existing User.")
    parser.add_argument("username", type=str, help="The username of the clinician to upgrade to Admin")
    
    args = parser.parse_args()
    create_admin(args.username)
