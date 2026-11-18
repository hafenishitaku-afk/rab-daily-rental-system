import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")


def fix_users_table():
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        print("✅ Connected. Adding missing worker columns to 'users' table...\n")
        
        # Add ALL potential missing worker columns safely
        columns_to_add = [
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS phone TEXT;",
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS job_title TEXT;",
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS specialty TEXT;",
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS hire_date TIMESTAMP;",
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS photo_path TEXT;",
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS salary REAL DEFAULT 0;" 
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS twofa_required INTEGER DEFAULT 0;",
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS twofa_enabled INTEGER DEFAULT 0;"# <-- ADDED THIS
        ]
        
        for sql in columns_to_add:
            cursor.execute(sql)
            col_name = sql.split("ADD COLUMN IF NOT EXISTS")[1].split(" ")[0]
            print(f"✅ Added/Verified column: {col_name}")
            
        conn.commit()
        print("\n🎉 'users' table updated successfully! The /workers/1 page should now work.")
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    fix_users_table()