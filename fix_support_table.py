import os, psycopg2
from dotenv import load_dotenv
load_dotenv()
conn = psycopg2.connect(os.environ["DATABASE_URL"])
cur = conn.cursor()
cur.execute("""
    CREATE TABLE IF NOT EXISTS customer_support (
        id SERIAL PRIMARY KEY,
        customer_id INTEGER NOT NULL REFERENCES customers(id) ON DELETE CASCADE,
        user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
        sender_role TEXT NOT NULL,
        file_path TEXT NOT NULL,
        resolved BOOLEAN DEFAULT FALSE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
""")
cur.execute("CREATE INDEX IF NOT EXISTS idx_support_cust ON customer_support(customer_id);")
conn.commit()
print("✅ customer_support table created.")
conn.close()