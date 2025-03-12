#!/usr/bin/env python
"""
Reset Database Script

This script will completely drop and recreate the database schema for ScholarScribe.
Warning: This will delete all data!
"""
import os
import sys
import time
import psycopg2
from dotenv import load_dotenv

def get_connection_string():
    """Get connection string from DATABASE_URL environment variable"""
    load_dotenv()
    
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("ERROR: DATABASE_URL environment variable is not set.")
        sys.exit(1)
        
    print(f"Using DATABASE_URL: {database_url}")
    return database_url

def reset_database():
    """
    Reset the database by dropping all existing tables
    """
    try:
        # Get connection string
        conn_string = get_connection_string()
        
        # Connect to database
        print("Connecting to database...")
        conn = psycopg2.connect(conn_string)
        conn.autocommit = True
        
        # Create a cursor
        cursor = conn.cursor()
        
        # Drop all enums
        print("Dropping enum types...")
        cursor.execute("""
        DO $$
        DECLARE
            enum_type text;
        BEGIN
            FOR enum_type IN (SELECT t.typname FROM pg_type t JOIN pg_catalog.pg_namespace n ON n.oid = t.typnamespace WHERE n.nspname = 'public' AND t.typtype = 'e')
            LOOP
                EXECUTE 'DROP TYPE IF EXISTS ' || enum_type || ' CASCADE';
            END LOOP;
        END
        $$;
        """)
        
        # Drop all tables
        print("Dropping all tables...")
        cursor.execute("""
        DO $$ 
        DECLARE
            r RECORD;
        BEGIN
            FOR r IN (SELECT tablename FROM pg_tables WHERE schemaname = 'public') 
            LOOP
                EXECUTE 'DROP TABLE IF EXISTS ' || r.tablename || ' CASCADE';
            END LOOP;
        END $$;
        """)
        
        # Close connection
        cursor.close()
        conn.close()
        
        print("Database reset successfully. All tables and enums dropped.")
        print("You can now run migrations to recreate the database schema.")
        
    except Exception as e:
        print(f"ERROR: Failed to reset database: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    print("WARNING: This will delete all data in the database!")
    print("Wait 5 seconds to cancel (Ctrl+C)...")
    try:
        time.sleep(5)
        reset_database()
    except KeyboardInterrupt:
        print("\nOperation cancelled.")
        sys.exit(0)