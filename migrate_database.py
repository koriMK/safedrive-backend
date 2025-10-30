#!/usr/bin/env python3
"""
Database Migration Script
Adds missing columns to existing database
"""

import os
import psycopg2
from urllib.parse import urlparse

def migrate_database():
    """Add missing columns to existing database"""
    
    # Get database URL from environment
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        print("❌ DATABASE_URL not found in environment")
        return False
    
    try:
        # Parse database URL
        url = urlparse(database_url)
        
        # Connect to database
        conn = psycopg2.connect(
            host=url.hostname,
            port=url.port,
            database=url.path[1:],  # Remove leading slash
            user=url.username,
            password=url.password
        )
        
        cursor = conn.cursor()
        
        print("🔄 Starting database migration...")
        
        # Check if columns exist and add if missing
        migrations = [
            {
                'table': 'users',
                'column': 'is_online',
                'sql': 'ALTER TABLE users ADD COLUMN is_online BOOLEAN DEFAULT FALSE;'
            },
            {
                'table': 'users', 
                'column': 'last_seen',
                'sql': 'ALTER TABLE users ADD COLUMN last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP;'
            }
        ]
        
        for migration in migrations:
            try:
                # Check if column exists
                cursor.execute("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name = %s AND column_name = %s;
                """, (migration['table'], migration['column']))
                
                if cursor.fetchone() is None:
                    # Column doesn't exist, add it
                    cursor.execute(migration['sql'])
                    print(f"✅ Added column {migration['column']} to {migration['table']}")
                else:
                    print(f"ℹ️ Column {migration['column']} already exists in {migration['table']}")
                    
            except Exception as e:
                print(f"❌ Error adding {migration['column']}: {e}")
                conn.rollback()
                return False
        
        # Commit all changes
        conn.commit()
        cursor.close()
        conn.close()
        
        print("🎉 Database migration completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Database migration failed: {e}")
        return False

if __name__ == '__main__':
    migrate_database()