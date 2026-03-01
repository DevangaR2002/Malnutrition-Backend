import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()
db_url = os.getenv("DATABASE_URL", "postgresql://postgres:BBB_54321@localhost:5432/malnutrition_db")

try:
    conn = psycopg2.connect(db_url)
    cur = conn.cursor()
    cur.execute("""
        SELECT column_name, data_type 
        FROM information_schema.columns 
        WHERE table_name='predictions';
    """)
    columns = cur.fetchall()
    print("Columns in predictions:")
    for col in columns:
        print(f" - {col[0]} ({col[1]})")
    cur.close()
    conn.close()
except Exception as e:
    print(f"Error: {e}")
