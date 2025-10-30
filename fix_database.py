#!/usr/bin/env python3
"""
Quick database fix for missing columns
"""

from app import create_app
from models import db
from sqlalchemy import text

def fix_database():
    """Add missing columns to existing database"""
    
    app = create_app()
    with app.app_context():
        try:
            print("🔄 Checking database schema...")
            
            # Check if columns exist
            result = db.engine.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'users' AND column_name IN ('is_online', 'last_seen');
            """))
            
            existing_columns = [row[0] for row in result]
            
            # Add missing columns
            if 'is_online' not in existing_columns:
                db.engine.execute(text("ALTER TABLE users ADD COLUMN is_online BOOLEAN DEFAULT FALSE;"))
                print("✅ Added is_online column")
            
            if 'last_seen' not in existing_columns:
                db.engine.execute(text("ALTER TABLE users ADD COLUMN last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP;"))
                print("✅ Added last_seen column")
            
            print("🎉 Database schema updated successfully!")
            return True
            
        except Exception as e:
            print(f"❌ Database fix failed: {e}")
            return False

if __name__ == '__main__':
    fix_database()