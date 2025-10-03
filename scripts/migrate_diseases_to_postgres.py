#!/usr/bin/env python3
"""
Migrate disease_reference table from SQLite to PostgreSQL

This script:
1. Reads all disease data from local SQLite database
2. Creates the disease_reference table in PostgreSQL
3. Imports all 12,252 diseases into PostgreSQL
"""

import os
import sys
import sqlite3
import psycopg2
from psycopg2.extras import execute_batch
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def get_postgres_url():
    """Get PostgreSQL connection URL from environment"""
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        raise ValueError("DATABASE_URL environment variable not set")

    # psycopg2 expects the URL as-is with postgresql://
    return db_url

def create_table_postgres(cursor):
    """Create disease_reference table in PostgreSQL"""

    # Drop table if exists
    cursor.execute("DROP TABLE IF EXISTS disease_reference CASCADE;")

    # Create table
    create_sql = """
    CREATE TABLE disease_reference (
        mondo_id VARCHAR(50) PRIMARY KEY,
        disease_name VARCHAR(300) NOT NULL,
        disease_synonyms TEXT,
        icd10_codes TEXT,
        snomed_code VARCHAR(20),
        umls_code VARCHAR(20),
        orphanet_code VARCHAR(20),
        short_description TEXT,
        disease_category VARCHAR(100),
        is_rare_disease BOOLEAN,
        estimated_prevalence VARCHAR(100),
        medlineplus_url VARCHAR(500),
        pubmed_search_url VARCHAR(500),
        mondo_url VARCHAR(500),
        search_count TEXT,
        last_searched_at TIMESTAMP,
        promoted_to_full_library BOOLEAN,
        promotion_date TIMESTAMP,
        data_source VARCHAR(50),
        imported_at TIMESTAMP,
        last_updated_at TIMESTAMP,
        is_billable BOOLEAN DEFAULT TRUE,
        billable_note VARCHAR(200)
    );
    """
    cursor.execute(create_sql)

    # Create indexes
    indexes = [
        "CREATE INDEX ix_disease_reference_disease_name ON disease_reference (disease_name);",
        "CREATE INDEX ix_disease_reference_snomed_code ON disease_reference (snomed_code);",
        "CREATE INDEX idx_rare_disease ON disease_reference (is_rare_disease);",
        "CREATE INDEX idx_icd10_lookup ON disease_reference (icd10_codes);",
        "CREATE INDEX idx_category ON disease_reference (disease_category);",
    ]

    for index_sql in indexes:
        cursor.execute(index_sql)

    print("✅ Created disease_reference table in PostgreSQL")

def migrate_data():
    """Main migration function"""

    print("🔄 Starting disease data migration from SQLite to PostgreSQL...")

    # Connect to SQLite
    sqlite_db = "ai_nurse_florence.db"
    if not os.path.exists(sqlite_db):
        raise FileNotFoundError(f"SQLite database not found: {sqlite_db}")

    sqlite_conn = sqlite3.connect(sqlite_db)
    sqlite_cursor = sqlite_conn.cursor()

    # Get PostgreSQL connection
    pg_url = get_postgres_url()
    pg_conn = psycopg2.connect(pg_url)
    pg_cursor = pg_conn.cursor()

    try:
        # Create table in PostgreSQL
        create_table_postgres(pg_cursor)
        pg_conn.commit()

        # Count records in SQLite
        sqlite_cursor.execute("SELECT COUNT(*) FROM disease_reference")
        total_count = sqlite_cursor.fetchone()[0]
        print(f"📊 Found {total_count:,} diseases in SQLite database")

        # Fetch all data from SQLite
        sqlite_cursor.execute("""
            SELECT mondo_id, disease_name, disease_synonyms, icd10_codes,
                   snomed_code, umls_code, orphanet_code, short_description,
                   disease_category, is_rare_disease, estimated_prevalence,
                   medlineplus_url, pubmed_search_url, mondo_url, search_count,
                   last_searched_at, promoted_to_full_library, promotion_date,
                   data_source, imported_at, last_updated_at, is_billable, billable_note
            FROM disease_reference
            ORDER BY mondo_id
        """)

        rows = sqlite_cursor.fetchall()
        print(f"📥 Fetched {len(rows):,} records from SQLite")

        # Convert SQLite data to PostgreSQL format (SQLite uses integers for booleans)
        converted_rows = []
        for row in rows:
            row_list = list(row)
            # Convert boolean fields (index 9: is_rare_disease, 16: promoted_to_full_library, 21: is_billable)
            if row_list[9] is not None:  # is_rare_disease
                row_list[9] = bool(row_list[9])
            if row_list[16] is not None:  # promoted_to_full_library
                row_list[16] = bool(row_list[16])
            if row_list[21] is not None:  # is_billable
                row_list[21] = bool(row_list[21])
            converted_rows.append(tuple(row_list))

        print(f"✓ Converted boolean fields from SQLite integers to PostgreSQL booleans")

        # Insert into PostgreSQL in batches
        insert_sql = """
            INSERT INTO disease_reference (
                mondo_id, disease_name, disease_synonyms, icd10_codes,
                snomed_code, umls_code, orphanet_code, short_description,
                disease_category, is_rare_disease, estimated_prevalence,
                medlineplus_url, pubmed_search_url, mondo_url, search_count,
                last_searched_at, promoted_to_full_library, promotion_date,
                data_source, imported_at, last_updated_at, is_billable, billable_note
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            )
        """

        batch_size = 1000
        for i in range(0, len(converted_rows), batch_size):
            batch = converted_rows[i:i + batch_size]
            execute_batch(pg_cursor, insert_sql, batch)
            pg_conn.commit()
            print(f"📤 Inserted {min(i + batch_size, len(converted_rows)):,}/{len(converted_rows):,} records...")

        # Verify migration
        pg_cursor.execute("SELECT COUNT(*) FROM disease_reference")
        pg_count = pg_cursor.fetchone()[0]

        print(f"\n✅ Migration completed successfully!")
        print(f"   SQLite records: {total_count:,}")
        print(f"   PostgreSQL records: {pg_count:,}")

        if pg_count == total_count:
            print("   ✅ Record counts match!")
        else:
            print("   ⚠️  Warning: Record counts don't match!")

        # Show sample data
        pg_cursor.execute("""
            SELECT disease_name, mondo_id, disease_category
            FROM disease_reference
            LIMIT 5
        """)
        samples = pg_cursor.fetchall()
        print("\n📋 Sample diseases in PostgreSQL:")
        for name, mondo_id, category in samples:
            print(f"   - {name} ({mondo_id}) [{category}]")

    except Exception as e:
        print(f"❌ Migration failed: {e}")
        pg_conn.rollback()
        raise

    finally:
        sqlite_conn.close()
        pg_conn.close()

if __name__ == "__main__":
    migrate_data()
