import os
import psycopg2
from dotenv import load_dotenv

# Load your .env file to get the DATABASE_URL
load_dotenv()

print("🔌 Connecting to database...")
conn = psycopg2.connect(os.environ["DATABASE_URL"])
cur = conn.cursor()

print("🔧 Adding missing columns to daily_rentals table...")
cur.execute("ALTER TABLE daily_rentals ADD COLUMN IF NOT EXISTS paused_seconds INTEGER DEFAULT 0;")
cur.execute("ALTER TABLE daily_rentals ADD COLUMN IF NOT EXISTS is_paused BOOLEAN DEFAULT FALSE;")
cur.execute("ALTER TABLE daily_rentals ADD COLUMN IF NOT EXISTS paused_since TIMESTAMP;")

conn.commit()
print("✅ Success! All pause-related columns are now in the database.")
conn.close()