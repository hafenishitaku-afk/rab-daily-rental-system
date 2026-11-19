import psycopg2
import csv
import os

# 👇 PASTE YOUR EXTERNAL DATABASE URL HERE, ENDING WITH /rental_db
DATABASE_URL = "postgresql://rab_main_db_user:hNYrV6OfYmxNDw5ZvQdNZe4d3d1sGbqy@dpg-dbne3m0u01pc73cgn5rg-a.virginia-postgres.render.com/rental_db"

# The order matters because of Foreign Keys!
# (e.g., you can't add a rental if the customer doesn't exist yet)
TABLES = [
    "users",
    "customers",
    "bicycles",
    "branches",
    "daily_rentals",
    "rental_payments",
    "damage_claims",
    "items"
]

def restore_table(conn, table_name):
    filename = f"backup_{table_name}.csv"
    
    if not os.path.exists(filename):
        print(f"⚠️ File {filename} not found. Skipping.")
        return

    print(f"Restoring {table_name} from {filename}...")
    
    with open(filename, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        headers = next(reader)
        
        # Build the SQL query dynamically based on CSV headers
        placeholders = ', '.join(['%s'] * len(headers))
        columns = ', '.join(headers)
        
        # Use ON CONFLICT DO NOTHING to prevent crashes if a row already exists
        # We assume the 'id' is the primary key for all tables
        sql = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders}) ON CONFLICT (id) DO NOTHING"
        
        cursor = conn.cursor()
        row_count = 0
        
        for row in reader:
            try:
                # Convert empty strings to None (NULL in database)
                clean_row = [None if val == '' else val for val in row]
                cursor.execute(sql, clean_row)
                row_count += 1
            except Exception as e:
                print(f"❌ Error inserting row into {table_name}: {e}")
                conn.rollback()
                cursor.execute("SET TRANSACTION ISOLATION LEVEL READ COMMITTED")
                continue
        
        conn.commit()
        cursor.close()
        print(f"✅ Successfully restored {row_count} rows into {table_name}")

def main():
    print("Connecting to database...")
    try:
        conn = psycopg2.connect(DATABASE_URL)
        print("Connected!")
        
        for table in TABLES:
            restore_table(conn, table)
            
        conn.close()
        print("🎉 All data restored successfully!")
        
    except Exception as e:
        print(f"❌ Database connection failed: {e}")

if __name__ == "__main__":
    main()