import psycopg2
from urllib.parse import urlparse

# 👇 PASTE YOUR EXTERNAL DATABASE URL HERE (The one you got from Render)
# It usually looks like: postgresql://user:pass@host:port/default_db_name
DATABASE_URL = "postgresql://rab_main_db_zfau_user:PcDKjTvwlBeKzli1F1DPv2Cq07pmLmws@dpg-dbua0nsipgvc73e04kig-a.virginia-postgres.render.com/rab_main_db_zfau"

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