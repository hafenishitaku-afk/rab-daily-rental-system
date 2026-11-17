import psycopg2
from werkzeug.security import generate_password_hash

import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")


def create_admin():
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    
    # Check if admin exists
    cursor.execute("SELECT id FROM users WHERE username = 'admin'")
    if cursor.fetchone():
        print("ℹ️ Admin user already exists.")
    else:
        print("Creating admin user...")
        hashed_pw = generate_password_hash("admin123")
        cursor.execute(
            "INSERT INTO users (username, password_hash, role, full_name) VALUES (%s, %s, %s, %s)",
            ("admin", hashed_pw, "admin", "System Administrator")
        )
        conn.commit()
        print("✅ Admin user created successfully!")
        
    cursor.close()
    conn.close()

if __name__ == "__main__":
    create_admin()