import os
import psycopg2
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()
DATABASE_URL = os.environ.get("DATABASE_URL")

def create_appointments_table():
    try:
        print("🔌 Connecting to database...")
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        
        print("🔨 Creating 'appointments' table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS appointments (
                id SERIAL PRIMARY KEY,
                staff_id INTEGER NOT NULL,
                manager_id INTEGER NOT NULL,
                reason TEXT NOT NULL,
                requested_time TEXT NOT NULL,
                status TEXT DEFAULT 'Pending', 
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (staff_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (manager_id) REFERENCES users(id) ON DELETE CASCADE
            );
        """)
        
        conn.commit()
        print("✅ 'appointments' table created successfully!")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    create_appointments_table()