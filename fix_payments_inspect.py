import os, psycopg2
from dotenv import load_dotenv
load_dotenv()
conn = psycopg2.connect(os.environ["DATABASE_URL"])
cur = conn.cursor()
cur.execute("""
    SELECT id, daily_rental_id, amount, payment_method, payment_date
    FROM rental_payments ORDER BY id
""")
print(f"{'id':>4} {'rental':>7} {'amount':>10}  method / date")
for r in cur.fetchall():
    print(f"{r[0]:>4} {str(r[1]):>7} {r[2]:>10}  {r[3]} / {r[4]}")
conn.close()