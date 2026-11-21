import os
import psycopg2
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()
DATABASE_URL = os.environ.get("DATABASE_URL")

def fix_tables():
    try:
        print("🔌 Connecting to live database...")
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        
        print("🔨 Creating 'announcement_voice_notes' table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS announcement_voice_notes (
                id SERIAL PRIMARY KEY,
                announcement_id INTEGER,
                user_id INTEGER NOT NULL,
                file_path TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        print("🔨 Creating 'bike_parts' table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS bike_parts (
                id SERIAL PRIMARY KEY,
                part_name TEXT NOT NULL,
                description TEXT,
                image_path TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        conn.commit()
        print("✅ Tables created successfully! The app will now work.")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    fix_tables()