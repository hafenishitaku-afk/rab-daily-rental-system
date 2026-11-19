import os
import psycopg2
from dotenv import load_dotenv

# 1. Load variables from the .env file (only works locally)
load_dotenv()

# 2. Read the URL from the environment
DATABASE_URL = os.environ.get("DATABASE_URL")

# 3. Safety check: Crash early with a helpful message if it's missing
if not DATABASE_URL:
    print("❌ ERROR: DATABASE_URL is missing!")
    print("Please create a .env file with your DATABASE_URL, or set it in your Render Dashboard.")
    exit(1)


# The tables where we use SERIAL (auto-increment) IDs
TABLES = [
    "users", "customers", "bicycles", "branches", 
    "daily_rentals", "rental_payments", "damage_claims", "items"
]

def fix_sequences():
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    
    for table in TABLES:
        try:
            # This command tells Postgres: "Find the highest ID in the table, 
            # and make sure the next auto-increment ID starts after that."
            sql = f"""
                SELECT setval(
                    pg_get_serial_sequence('{table}', 'id'),
                    COALESCE((SELECT MAX(id) FROM {table}), 1)
                );
            """
            cursor.execute(sql)
            print(f"✅ Fixed sequence for {table}")
        except Exception as e:
            print(f"❌ Could not fix sequence for {table}: {e}")
            conn.rollback()
            
    conn.commit()
    cursor.close()
    conn.close()
    print("🎉 All sequences updated!")

if __name__ == "__main__":
    fix_sequences()