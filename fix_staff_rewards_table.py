import os, psycopg2
from dotenv import load_dotenv
load_dotenv()
conn = psycopg2.connect(os.environ["DATABASE_URL"])
cur = conn.cursor()
cur.execute("""
    CREATE TABLE IF NOT EXISTS staff_rewards (
        id SERIAL PRIMARY KEY,
        staff_id INTEGER NOT NULL,
        reward_type TEXT NOT NULL,
        amount NUMERIC DEFAULT 0,
        reason TEXT,
        granted_by INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
""")
conn.commit()
print("✅ staff_rewards table created.")
conn.close()