import sys
import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

def create_rental_tables():
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        print("✅ Connected to rental_db. Creating tables...\n")
    except Exception as e:
        print(f"❌ Failed to connect to database: {e}")
        sys.exit(1)

    # Ordered specifically to respect Foreign Key dependencies
    tables = [
        # 1. Core Identity & Access
        """CREATE TABLE IF NOT EXISTS users(
            id SERIAL PRIMARY KEY, username TEXT UNIQUE NOT NULL, password_hash TEXT NOT NULL, 
            role TEXT DEFAULT 'staff', full_name TEXT, email TEXT, branch_id INTEGER, 
            phone TEXT, job_title TEXT, specialty TEXT, hire_date TIMESTAMP, photo_path TEXT, salary REAL DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, 
            twofa_required INTEGER DEFAULT 0, twofa_enabled INTEGER DEFAULT 0
        );""",
        
        """CREATE TABLE IF NOT EXISTS login_attempts(
            user_id INTEGER PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE, 
            failed_count INTEGER DEFAULT 0, last_failed_at TIMESTAMP, 
            locked_until TIMESTAMP, locked_reason TEXT
        );""",
        
        """CREATE TABLE IF NOT EXISTS user_2fa(
            user_id INTEGER PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE, 
            secret TEXT NOT NULL, enabled INTEGER DEFAULT 0, 
            confirmed_at TIMESTAMP, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );""",
        
        """CREATE TABLE IF NOT EXISTS user_2fa_backup_codes(
            id SERIAL PRIMARY KEY, user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE, 
            code_hash TEXT NOT NULL, used_at TIMESTAMP, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );""",

        # 2. Branch & Staff Operations
        """CREATE TABLE IF NOT EXISTS branches(
            id SERIAL PRIMARY KEY, name TEXT NOT NULL, location TEXT, address TEXT, 
            phone TEXT, email TEXT, manager_id INTEGER REFERENCES users(id) ON DELETE SET NULL, 
            is_active INTEGER DEFAULT 1, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );""",
        
        """CREATE TABLE IF NOT EXISTS worker_documents(
            id SERIAL PRIMARY KEY, user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE, 
            document_type TEXT NOT NULL, file_path TEXT NOT NULL, 
            uploaded_by_user_id INTEGER REFERENCES users(id) ON DELETE SET NULL, 
            uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, notes TEXT
        );""",

        # 3. Customer Management
        """CREATE TABLE IF NOT EXISTS pending_registrations(
            id SERIAL PRIMARY KEY, full_name TEXT NOT NULL, id_number TEXT, phone TEXT NOT NULL, 
            email TEXT, address TEXT, gender TEXT, id_photo_path TEXT, customer_photo_path TEXT, 
            signature_data TEXT, terms_accepted INTEGER DEFAULT 0, status TEXT DEFAULT 'Pending', 
            rejection_reason TEXT, reviewed_by INTEGER, reviewed_at TIMESTAMP
        );""",
        
        """CREATE TABLE IF NOT EXISTS customers(
            id SERIAL PRIMARY KEY, full_name TEXT NOT NULL, id_number TEXT, phone TEXT NOT NULL, 
            email TEXT, address TEXT, user_id INTEGER REFERENCES users(id) ON DELETE SET NULL, 
            terms_accepted INTEGER DEFAULT 0, terms_accepted_date TIMESTAMP, signature_data TEXT, 
            verification_status TEXT DEFAULT 'Pending', verification_notes TEXT, 
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );""",
        
        """CREATE TABLE IF NOT EXISTS customer_documents(
            id SERIAL PRIMARY KEY, customer_id INTEGER NOT NULL REFERENCES customers(id) ON DELETE CASCADE, 
            document_type TEXT NOT NULL, file_path TEXT NOT NULL, uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );""",
        
        """CREATE TABLE IF NOT EXISTS verification_requests(
            id SERIAL PRIMARY KEY, customer_id INTEGER NOT NULL REFERENCES customers(id) ON DELETE CASCADE, 
            verified_by INTEGER REFERENCES users(id) ON DELETE SET NULL, status TEXT DEFAULT 'Pending', 
            notes TEXT, verified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );""",

        # 4. Rental Core Operations
        """CREATE TABLE IF NOT EXISTS bicycles(
            id SERIAL PRIMARY KEY, bike_code TEXT UNIQUE NOT NULL, brand TEXT, model TEXT, 
            bike_type TEXT DEFAULT 'Standard', hourly_rate REAL DEFAULT 60, daily_cap REAL DEFAULT 480, 
            deposit_amount REAL DEFAULT 50, status TEXT DEFAULT 'Available', 
            branch_id INTEGER REFERENCES branches(id), notes TEXT, condition_notes TEXT
        );""",
        
        """CREATE TABLE IF NOT EXISTS daily_rates(
            id SERIAL PRIMARY KEY, bike_type TEXT, hourly_rate REAL DEFAULT 60, 
            daily_cap REAL DEFAULT 480, deposit REAL DEFAULT 50, is_active INTEGER DEFAULT 1
        );""",
        
        """CREATE TABLE IF NOT EXISTS items(
            id SERIAL PRIMARY KEY, name TEXT UNIQUE NOT NULL, description TEXT, 
            is_active INTEGER DEFAULT 1, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );""",
        
        """CREATE TABLE IF NOT EXISTS daily_rentals(
            id SERIAL PRIMARY KEY, customer_id INTEGER NOT NULL REFERENCES customers(id), 
            bicycle_id INTEGER NOT NULL REFERENCES bicycles(id), branch_id INTEGER REFERENCES branches(id), 
            start_time TIMESTAMP NOT NULL, end_time TIMESTAMP, actual_return_time TIMESTAMP, 
            total_hours REAL, total_cost REAL, hourly_rate REAL, daily_cap REAL, 
            deposit_paid REAL DEFAULT 0, late_fee REAL DEFAULT 0, discount_code_id INTEGER, 
            discount_amount REAL DEFAULT 0, payment_status TEXT DEFAULT 'Pending', 
            payment_method TEXT, status TEXT DEFAULT 'Active', condition_before TEXT, 
            condition_after TEXT, agreement_signed INTEGER DEFAULT 0, notes TEXT, 
            start_condition_note TEXT, damage_charge REAL DEFAULT 0, 
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );""",
        
        """CREATE TABLE IF NOT EXISTS rental_items(
            id SERIAL PRIMARY KEY, rental_id INTEGER NOT NULL REFERENCES daily_rentals(id) ON DELETE CASCADE, 
            item_id INTEGER NOT NULL REFERENCES items(id), 
            given_by_user_id INTEGER REFERENCES users(id) ON DELETE SET NULL, 
            given_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, 
            returned_by_user_id INTEGER REFERENCES users(id) ON DELETE SET NULL, 
            returned_at TIMESTAMP, condition_on_return TEXT, notes TEXT, UNIQUE(rental_id, item_id)
        );""",
        
        """CREATE TABLE IF NOT EXISTS rental_payments(
            id SERIAL PRIMARY KEY, daily_rental_id INTEGER NOT NULL REFERENCES daily_rentals(id) ON DELETE CASCADE, 
            amount REAL NOT NULL, payment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP, 
            payment_method TEXT, status TEXT DEFAULT 'Completed'
        );""",
        
        """CREATE TABLE IF NOT EXISTS damage_claims(
            id SERIAL PRIMARY KEY, rental_id INTEGER REFERENCES daily_rentals(id) ON DELETE SET NULL, 
            customer_id INTEGER NOT NULL REFERENCES customers(id) ON DELETE CASCADE, 
            bicycle_id INTEGER REFERENCES bicycles(id) ON DELETE SET NULL, 
            item_id INTEGER REFERENCES items(id) ON DELETE SET NULL, description TEXT NOT NULL, 
            amount REAL NOT NULL DEFAULT 0, status TEXT DEFAULT 'Pending', 
            charged_by_user_id INTEGER REFERENCES users(id) ON DELETE SET NULL, 
            charged_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, paid_at TIMESTAMP, 
            payment_method TEXT, signature_data TEXT, signed_agreement_path TEXT, notes TEXT
        );""",

        # 5. Fleet Maintenance & Health
        """CREATE TABLE IF NOT EXISTS maintenance_records(
            id SERIAL PRIMARY KEY, bicycle_id INTEGER NOT NULL REFERENCES bicycles(id) ON DELETE CASCADE, 
            maintenance_type TEXT NOT NULL, description TEXT, cost REAL DEFAULT 0, 
            status TEXT DEFAULT 'Scheduled', scheduled_date TIMESTAMP, completed_date TIMESTAMP, 
            performed_by TEXT, notes TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );""",
        
        """CREATE TABLE IF NOT EXISTS bike_conditions(
            id SERIAL PRIMARY KEY, bicycle_id INTEGER NOT NULL REFERENCES bicycles(id) ON DELETE CASCADE, 
            condition_type TEXT NOT NULL, condition_status TEXT NOT NULL, notes TEXT, 
            checked_by INTEGER REFERENCES users(id) ON DELETE SET NULL, 
            checked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, 
            rental_id INTEGER REFERENCES daily_rentals(id) ON DELETE CASCADE
        );""",
        
        """CREATE TABLE IF NOT EXISTS bicycle_health(
            id SERIAL PRIMARY KEY, bicycle_id INTEGER NOT NULL REFERENCES bicycles(id) ON DELETE CASCADE, 
            health_score INTEGER DEFAULT 100, condition_rating TEXT DEFAULT 'Excellent', 
            last_maintenance_date TIMESTAMP, next_maintenance_due TIMESTAMP, 
            total_maintenance_count INTEGER DEFAULT 0, total_repair_cost REAL DEFAULT 0, 
            last_condition_check TIMESTAMP, notes TEXT, updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );""",
        
        """CREATE TABLE IF NOT EXISTS bicycle_health_history(
            id SERIAL PRIMARY KEY, bicycle_id INTEGER NOT NULL REFERENCES bicycles(id) ON DELETE CASCADE, 
            health_score INTEGER NOT NULL, condition_rating TEXT NOT NULL, reason TEXT, 
            recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );""",

        # 6. Loyalty & Discounts
        """CREATE TABLE IF NOT EXISTS discount_codes(
            id SERIAL PRIMARY KEY, code TEXT UNIQUE NOT NULL, description TEXT, 
            discount_type TEXT NOT NULL, discount_value REAL NOT NULL, min_rental_amount REAL DEFAULT 0, 
            max_uses INTEGER DEFAULT 0, used_count INTEGER DEFAULT 0, start_date TIMESTAMP, 
            end_date TIMESTAMP, is_active INTEGER DEFAULT 1, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );""",
        
        """CREATE TABLE IF NOT EXISTS discount_usage(
            id SERIAL PRIMARY KEY, discount_code_id INTEGER NOT NULL REFERENCES discount_codes(id), 
            rental_id INTEGER NOT NULL REFERENCES daily_rentals(id) ON DELETE CASCADE, 
            customer_id INTEGER NOT NULL REFERENCES customers(id) ON DELETE CASCADE, 
            amount_discounted REAL NOT NULL, used_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );""",
        
        """CREATE TABLE IF NOT EXISTS loyalty_points(
            id SERIAL PRIMARY KEY, customer_id INTEGER NOT NULL REFERENCES customers(id) ON DELETE CASCADE, 
            points INTEGER DEFAULT 0, total_spent REAL DEFAULT 0, total_rentals INTEGER DEFAULT 0, 
            tier TEXT DEFAULT 'Bronze', updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );""",
        
        """CREATE TABLE IF NOT EXISTS points_transactions(
            id SERIAL PRIMARY KEY, customer_id INTEGER NOT NULL REFERENCES customers(id) ON DELETE CASCADE, 
            points INTEGER NOT NULL, transaction_type TEXT NOT NULL, description TEXT, 
            rental_id INTEGER REFERENCES daily_rentals(id) ON DELETE CASCADE, 
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );""",

        # 7. Security, Compliance & Auditing
        """CREATE TABLE IF NOT EXISTS login_history(
            id SERIAL PRIMARY KEY, user_id INTEGER REFERENCES users(id) ON DELETE SET NULL, 
            username_attempted TEXT, success INTEGER DEFAULT 0, ip_address TEXT, 
            user_agent TEXT, device_summary TEXT, failure_reason TEXT, 
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );""",
        
        """CREATE TABLE IF NOT EXISTS audit_log(
            id SERIAL PRIMARY KEY, user_id INTEGER REFERENCES users(id) ON DELETE SET NULL, 
            username TEXT, user_role TEXT, action TEXT NOT NULL, entity_type TEXT, 
            entity_id INTEGER, details TEXT, ip_address TEXT, user_agent TEXT, 
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );""",
        
        """CREATE TABLE IF NOT EXISTS document_views(
            id SERIAL PRIMARY KEY, document_id INTEGER NOT NULL REFERENCES customer_documents(id) ON DELETE CASCADE, 
            user_id INTEGER REFERENCES users(id) ON DELETE SET NULL, 
            viewed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, ip_address TEXT
        );""",
        
        """CREATE TABLE IF NOT EXISTS privacy_requests(
            id SERIAL PRIMARY KEY, customer_id INTEGER NOT NULL REFERENCES customers(id) ON DELETE CASCADE, 
            request_type TEXT NOT NULL, reason TEXT, status TEXT DEFAULT 'Pending', 
            reviewed_by_user_id INTEGER REFERENCES users(id) ON DELETE SET NULL, 
            reviewed_at TIMESTAMP, review_notes TEXT, requested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, 
            completed_at TIMESTAMP
        );""",

        # 8. Internal Communications & HR
        """CREATE TABLE IF NOT EXISTS announcements(
            id SERIAL PRIMARY KEY, title TEXT NOT NULL, content TEXT NOT NULL, 
            author_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE, 
            author_name TEXT NOT NULL, author_role TEXT NOT NULL, priority TEXT DEFAULT 'normal', 
            category TEXT DEFAULT 'general', is_pinned INTEGER DEFAULT 0, is_active INTEGER DEFAULT 1, 
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );""",
        
        """CREATE TABLE IF NOT EXISTS announcement_comments(
            id SERIAL PRIMARY KEY, announcement_id INTEGER NOT NULL REFERENCES announcements(id) ON DELETE CASCADE, 
            user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE, user_name TEXT NOT NULL, 
            user_role TEXT NOT NULL, comment TEXT NOT NULL, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );""",
        
        """CREATE TABLE IF NOT EXISTS announcement_reads(
            id SERIAL PRIMARY KEY, announcement_id INTEGER NOT NULL REFERENCES announcements(id) ON DELETE CASCADE, 
            user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE, 
            read_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, UNIQUE(announcement_id, user_id)
        );""",
        
        """CREATE TABLE IF NOT EXISTS suggestions(
            id SERIAL PRIMARY KEY, user_id INTEGER NOT NULL, user_name TEXT NOT NULL, 
            user_role TEXT NOT NULL, content_type TEXT NOT NULL, content TEXT, file_path TEXT, 
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );""",
        
        """CREATE TABLE IF NOT EXISTS warnings(
            id SERIAL PRIMARY KEY, user_id INTEGER, customer_id INTEGER, 
            issued_by_id INTEGER NOT NULL, level TEXT NOT NULL, reason TEXT NOT NULL, 
            status TEXT DEFAULT 'Unsigned', created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, signed_at TIMESTAMP
        );""",
        
        """CREATE TABLE IF NOT EXISTS awards(
            id SERIAL PRIMARY KEY, user_id INTEGER, customer_id INTEGER, 
            award_title TEXT NOT NULL, reason TEXT NOT NULL, issued_by_id INTEGER NOT NULL, 
            issued_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );""",

        # 9. System Utilities
        """CREATE TABLE IF NOT EXISTS reminder_logs(
            id SERIAL PRIMARY KEY, rental_id INTEGER NOT NULL REFERENCES daily_rentals(id) ON DELETE CASCADE, 
            reminder_type TEXT NOT NULL, sent_to TEXT NOT NULL, sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );"""
    ]

    success_count = 0
    for table_sql in tables:
        try:
            cursor.execute(table_sql)
            # Extract table name for clean printing
            table_name = table_sql.split("IF NOT EXISTS")[1].split("(")[0].strip()
            print(f"✅ Created: {table_name}")
            success_count += 1
        except Exception as e:
            print(f"❌ Error creating table: {e}")
            conn.rollback() 
            
    conn.commit()
    print(f"\n🎉 Done! Successfully verified/created {success_count} tables in rental_db.")
    cursor.close()
    conn.close()

if __name__ == "__main__":
    create_rental_tables()