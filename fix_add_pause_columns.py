import os, psycopg2
from dotenv import load_dotenv
load_dotenv()

conn = psycopg2.connect(os.environ["DATABASE_URL"])
cur = conn.cursor()

# Add columns if they don't exist
cur.execute("""
    ALTER TABLE daily_rentals 
    ADD COLUMN IF NOT EXISTS is_paused BOOLEAN DEFAULT FALSE,
    ADD COLUMN IF NOT EXISTS paused_since TIMESTAMP;
""")
conn.commit()
print("✅ Added is_paused and paused_since columns.")
conn.close()