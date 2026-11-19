import psycopg2
import os
from urllib.parse import urlparse
from dotenv import load_dotenv

# ✅ Load environment variables from .env file
load_dotenv()

# ✅ Read the URL from the environment (NOT hardcoded)
DATABASE_URL = os.environ.get("DATABASE_URL")

if not DATABASE_URL:
    print("❌ Error: DATABASE_URL environment variable is missing.")
    print("Make sure you have a .env file with DATABASE_URL=postgresql://...")
    exit(1)

def setup_databases():
    # Parse the URL to find out which database it currently connects to
    parsed = urlparse(DATABASE_URL)
    default_db = parsed.path.lstrip('/')
    
    # The two isolated databases we want to ensure exist
    target_dbs = ["rental_db", "community_db"]
    
    try:
        print(f"🔌 Connecting to base database: '{default_db}'...")
        conn = psycopg2.connect(DATABASE_URL)
        
        # ⚠️ CRITICAL: PostgreSQL requires autocommit to be True to run CREATE DATABASE
        conn.autocommit = True 
        cursor = conn.cursor()
        
        print("✅ Connected successfully. Checking databases...\n")
        
        for db_name in target_dbs:
            # If the URL already points to this database, it obviously exists
            if db_name == default_db:
                print(f"ℹ️ Database '{db_name}' is your default database (already exists).")
                continue
                
            # Check if the target database exists in PostgreSQL
            cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s;", (db_name,))
            
            if not cursor.fetchone():
                # Create the database if it doesn't exist
                cursor.execute(f"CREATE DATABASE {db_name};")
                print(f"✅ Successfully created database: {db_name}")
            else:
                print(f"ℹ️ Database '{db_name}' already exists.")
                
        cursor.close()
        conn.close()
        print("\n🎉 Main database setup complete! You now have isolated databases.")
        
    except Exception as e:
        print(f"❌ Error setting up databases: {e}")
        print("\n💡 Tip: Make sure your DATABASE_URL is correct and your Render database is active.")

if __name__ == "__main__":
    setup_databases()