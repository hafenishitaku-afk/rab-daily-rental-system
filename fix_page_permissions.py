import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.environ.get("DATABASE_URL")

def create_table():
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS page_permissions (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            page_key TEXT NOT NULL,
            can_view BOOLEAN DEFAULT FALSE,
            can_edit BOOLEAN DEFAULT FALSE,
            UNIQUE(user_id, page_key)
        );
    """)
    
    # Grant the admin (user_id=1) access to everything by default
    sensitive_pages = ['workers', 'audit_log_master', 'station_payouts', 'exports', 'users', 'profile']
    for page in sensitive_pages:
        cursor.execute("""
            INSERT INTO page_permissions (user_id, page_key, can_view, can_edit)
            VALUES (1, %s, TRUE, TRUE)
            ON CONFLICT (user_id, page_key) DO NOTHING;
        """, (page,))
    
    conn.commit()
    print("✅ page_permissions table created. Admin (user_id=1) has full access.")
    cursor.close()
    conn.close()

if __name__ == "__main__":
    create_table()