import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()
db_url = os.getenv("DATABASE_URL", "postgresql://postgres:BBB_54321@localhost:5432/malnutrition_db")

try:
    print(f"Connecting to database: {db_url}")
    conn = psycopg2.connect(db_url)
    conn.autocommit = True
    cur = conn.cursor()
    
    print("Flushing all legacy data from the predictions table...")
    # Using CASCADE handles the PredictionFeedback child table dependencies automatically 
    cur.execute("TRUNCATE TABLE predictions CASCADE;")
    
    print("Successfully deleted all past history from the database.")
    
    cur.close()
    conn.close()
except Exception as e:
    print(f"Error executing TRUNCATE: {e}")
