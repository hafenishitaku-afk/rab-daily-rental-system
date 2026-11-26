import os, psycopg2
from dotenv import load_dotenv
load_dotenv()
conn = psycopg2.connect(os.environ["DATABASE_URL"])
cur = conn.cursor()
cur.execute("""
    ALTER TABLE daily_rentals
    ADD COLUMN IF NOT EXISTS paused_seconds INTEGER DEFAULT 0;
""")
conn.commit()
print("✅ paused_seconds column added.")
conn.close()