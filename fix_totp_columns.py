import os
import psycopg2
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()
DATABASE_URL = os.environ.get("DATABASE_URL")

def fix_totp_columns():
    try:
        print("🔌 Connecting to database...")
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        
        print("🔨 Adding 2FA columns to 'users' table...")
        cursor.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS totp_secret TEXT;")
        cursor.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS totp_enabled BOOLEAN DEFAULT FALSE;")
        
        conn.commit()
        print("✅ 2FA columns added successfully!")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    fix_totp_columns()