import sys
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.user import User

def promote_user(username: str):
    db: Session = SessionLocal()
    try:
        user = db.query(User).filter(User.username == username).first()
        if not user:
            print(f"Error: User '{username}' not found in the database.")
            return

        if user.is_admin:
            print(f"User '{username}' is already an admin.")
            return

        user.is_admin = True
        db.commit()
        print(f"Success! User '{username}' has been promoted to Admin.")
        print("Please log out and log back in on the frontend to refresh your access token.")
        
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python promote_admin.py <username>")
        sys.exit(1)
        
    target_username = sys.argv[1]
    promote_user(target_username)
