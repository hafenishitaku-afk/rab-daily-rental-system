
import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")


def inspect_database():
    if not DATABASE_URL:
        print("ERROR: DATABASE_URL environment variable is missing.")
        return

    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()

    print("\n========== RAB DATABASE AUDIT ==========\n")

    # 1. List all existing tables
    cursor.execute("""
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = 'public'
          AND table_type = 'BASE TABLE'
        ORDER BY table_name;
    """)

    tables = cursor.fetchall()

    print(f"TOTAL TABLES FOUND: {len(tables)}\n")

    for (table_name,) in tables:
        print(f"\nTABLE: {table_name}")
        print("-" * 60)

        # 2. Inspect columns
        cursor.execute("""
            SELECT
                column_name,
                data_type,
                is_nullable,
                column_default
            FROM information_schema.columns
            WHERE table_schema = 'public'
              AND table_name = %s
            ORDER BY ordinal_position;
        """, (table_name,))

        columns = cursor.fetchall()

        for column in columns:
            name, data_type, nullable, default = column

            print(
                f"  {name} | {data_type} | "
                f"Nullable: {nullable} | Default: {default}"
            )

        # 3. Inspect foreign keys
        cursor.execute("""
            SELECT
                kcu.column_name,
                ccu.table_name AS referenced_table,
                ccu.column_name AS referenced_column
            FROM information_schema.key_column_usage kcu
            JOIN information_schema.constraint_column_usage ccu
                ON kcu.constraint_name = ccu.constraint_name
                AND kcu.constraint_schema = ccu.constraint_schema
            WHERE kcu.table_schema = 'public'
              AND kcu.table_name = %s
              AND kcu.position_in_unique_constraint IS NOT NULL;
        """, (table_name,))

        foreign_keys = cursor.fetchall()

        if foreign_keys:
            print("  FOREIGN KEYS:")
            for fk in foreign_keys:
                print(f"    {fk[0]} -> {fk[1]}.{fk[2]}")

    print("\n========== AUDIT COMPLETE ==========\n")

    cursor.close()
    conn.close()


if __name__ == "__main__":
    inspect_database()
