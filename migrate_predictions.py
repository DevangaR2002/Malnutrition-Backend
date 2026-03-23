import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def migrate():
    
    db_url = os.getenv("DATABASE_URL","postgresql://postgres:1234@localhost:5432/malnutrition_db" )
    print(f"Connecting to database: {db_url}")
    
    try:
        conn = psycopg2.connect(db_url)
        conn.autocommit = True
        cur = conn.cursor()
        
        print("Checking for user_id column in predictions table...")
        
        cur.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='predictions' AND column_name='user_id';
        """)
        
        if cur.fetchone():
            print("Column 'user_id' already exists in 'predictions' table.")
        else:
            print("Adding 'user_id' column to 'predictions' table...")
            cur.execute("ALTER TABLE predictions ADD COLUMN user_id INTEGER REFERENCES users(id);")
            print("Successfully added 'user_id' column.")
            
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Migration failed: {e}")

if __name__ == "__main__":
    migrate()
