import sqlite3
import os
from sqlalchemy import create_engine, text
from app.config import get_settings

try:
    # Get DB URL
    settings = get_settings()
    db_url = settings.database_url
    
    print(f"Applying migration to: {db_url}")
    
    if db_url.startswith("sqlite:///"):
        # SQLite
        db_path = db_url.replace("sqlite:///", "")
        db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), db_path)
        print(f"SQLite path: {db_path}")
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("ALTER TABLE users ADD COLUMN is_admin BOOLEAN DEFAULT FALSE;")
            conn.commit()
            print("Successfully added is_admin column to SQLite.")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e).lower():
                print("Column is_admin already exists in SQLite.")
            else:
                print(f"Error executing SQLite query: {e}")
                
        conn.close()
    
    elif db_url.startswith("postgresql://"):
        # PostgreSQL
        engine = create_engine(db_url)
        with engine.begin() as conn:
            try:
                conn.execute(text("ALTER TABLE users ADD COLUMN is_admin BOOLEAN DEFAULT FALSE;"))
                print("Successfully added is_admin column to PostgreSQL.")
            except Exception as e:
                 print(f"Column might already exist or error occurred: {e}")
                 
    else:
        print("Unsupported database URL scheme for this simple migration script.")

except Exception as e:
    print(f"Failed to migrate database: {e}")
