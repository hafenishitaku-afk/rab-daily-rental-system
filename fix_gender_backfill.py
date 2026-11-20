# fix_gender_backfill.py
import os, psycopg2
from dotenv import load_dotenv
load_dotenv()
conn = psycopg2.connect(os.environ["DATABASE_URL"])
cur = conn.cursor()
cur.execute("""
    UPDATE customers c
    SET gender = p.gender
    FROM pending_registrations p
    WHERE c.id_number = p.id_number
      AND (c.gender IS NULL OR c.gender = '')
      AND p.gender IS NOT NULL;
""")
conn.commit()
print(f"✅ Backfilled gender for {cur.rowcount} customer(s).")
conn.close()