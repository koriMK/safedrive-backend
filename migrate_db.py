#!/usr/bin/env python3
"""
Database migration script to remove is_online and last_seen columns from users table
"""

import os
from app import app
from models import db

def migrate_database():
    """Remove problematic columns from users table"""
    with app.app_context():
        try:
            # Check if columns exist and drop them
            print("Checking database schema...")
            
            # Try to drop the problematic columns
            with db.engine.connect() as conn:
                # Check if columns exist first
                result = conn.execute("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name = 'users' 
                    AND column_name IN ('is_online', 'last_seen')
                """)
                
                existing_columns = [row[0] for row in result]
                
                if 'is_online' in existing_columns:
                    print("Dropping is_online column...")
                    conn.execute("ALTER TABLE users DROP COLUMN is_online")
                    conn.commit()
                    print("✓ is_online column dropped")
                
                if 'last_seen' in existing_columns:
                    print("Dropping last_seen column...")
                    conn.execute("ALTER TABLE users DROP COLUMN last_seen")
                    conn.commit()
                    print("✓ last_seen column dropped")
                
                if not existing_columns:
                    print("✓ No problematic columns found - database is already correct")
                
            print("Database migration completed successfully!")
            
        except Exception as e:
            print(f"Migration error: {e}")
            # If columns don't exist, that's fine
            if "does not exist" in str(e):
                print("✓ Columns already removed - database is correct")
            else:
                raise

if __name__ == "__main__":
    migrate_database()