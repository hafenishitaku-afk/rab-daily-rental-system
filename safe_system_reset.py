import os
import psycopg2
from dotenv import load_dotenv

# Load your database credentials
load_dotenv()
DATABASE_URL = os.environ.get("DATABASE_URL")

def safe_reset():
    print("🔌 Connecting to database...")
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()

    # We use DELETE instead of TRUNCATE to safely respect Foreign Keys 
    # without accidentally deleting your Admin user via CASCADE.
    
    # 1. Wipe Rental & Financial Data
    print("🧹 Wiping rentals and payments...")
    cur.execute("DELETE FROM rental_items;")
    cur.execute("DELETE FROM rental_payments;")
    cur.execute("DELETE FROM daily_rentals;")

    # 2. Wipe Customer Data & Attachments
    print("🧹 Wiping customers and documents...")
    cur.execute("DELETE FROM customer_documents;")
    cur.execute("DELETE FROM loyalty_points;")
    cur.execute("DELETE FROM damage_claims;")
    cur.execute("DELETE FROM customer_support;")
    cur.execute("DELETE FROM customers;") # This leaves the 'users' accounts orphaned, which is fine.

    # 3. Wipe Bicycles & Maintenance
    print("🧹 Wiping bicycles and maintenance...")
    cur.execute("DELETE FROM bicycle_health;")
    cur.execute("DELETE FROM maintenance_records;")
    cur.execute("DELETE FROM bicycles;")

    # 4. Wipe Communications & Announcements
    print("🧹 Wiping announcements and voice notes...")
    cur.execute("DELETE FROM announcement_comments;")
    cur.execute("DELETE FROM announcement_voice_notes;")
    cur.execute("DELETE FROM announcements;")
    cur.execute("DELETE FROM announcement_reads;")

    # 5. Wipe Registrations & System Logs
    print("🧹 Wiping pending registrations and logs...")
    cur.execute("DELETE FROM pending_registrations;")
    cur.execute("DELETE FROM audit_log;")
    cur.execute("DELETE FROM login_attempts;")
    
    # 6. Wipe Training & Appointments
    print("🧹 Wiping training and appointments...")
    cur.execute("DELETE FROM bike_parts;")
    cur.execute("DELETE FROM appointments;")

    # 7. OPTIONAL: Wipe Customer User Accounts (Keep Staff/Admin/Manager)
    print("🧹 Wiping customer login accounts (keeping staff/admin)...")
    cur.execute("DELETE FROM users WHERE role = 'customer';")

    # Commit the changes
    conn.commit()
    
    # Reset the ID counters so new records start at 1 again (Optional but clean)
    print("🔄 Resetting ID sequences...")
    tables_to_reset = [
        'rental_items', 'rental_payments', 'daily_rentals', 'customer_documents',
        'loyalty_points', 'damage_claims', 'customer_support', 'customers',
        'bicycle_health', 'maintenance_records', 'bicycles', 'announcement_comments',
        'announcement_voice_notes', 'announcements', 'announcement_reads',
        'pending_registrations', 'audit_log', 'login_attempts', 'bike_parts', 'appointments'
    ]
    
    for table in tables_to_reset:
        try:
            # This gets the sequence name automatically in Postgres
            seq_name = f"{table}_id_seq"
            cur.execute(f"ALTER SEQUENCE {seq_name} RESTART WITH 1;")
        except Exception:
            pass # Ignore if sequence doesn't exist

    conn.commit()
    cur.close()
    conn.close()
    
    print("✅ SYSTEM SUCCESSFULLY RESET!")
    print("🔒 Your Admin/Staff accounts and Stations are safe. You can still log in.")

if __name__ == "__main__":
    # Safety confirmation
    confirm = input("⚠️  This will DELETE all business data. Type 'YES' to confirm: ")
    if confirm.upper() == 'YES':
        safe_reset()
    else:
        print("❌ Reset cancelled.")