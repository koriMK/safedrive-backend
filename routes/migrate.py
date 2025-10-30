from flask import Blueprint, jsonify
from models import db
import os

migrate_bp = Blueprint('migrate', __name__)

@migrate_bp.route('/migrate-db', methods=['POST'])
def migrate_database():
    """
    Emergency database migration endpoint
    ---
    tags:
      - System
    responses:
      200:
        description: Migration completed successfully
      403:
        description: Migration only allowed in production
      500:
        description: Migration failed
    """
    try:
        # Only allow in production with specific header
        if os.environ.get('FLASK_ENV') != 'production':
            return jsonify({'success': False, 'error': 'Migration only allowed in production'}), 403
        
        # Check if columns exist and drop them
        with db.engine.connect() as conn:
            # Check if columns exist first
            result = conn.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'users' 
                AND column_name IN ('is_online', 'last_seen')
            """)
            
            existing_columns = [row[0] for row in result]
            dropped_columns = []
            
            if 'is_online' in existing_columns:
                conn.execute("ALTER TABLE users DROP COLUMN is_online")
                dropped_columns.append('is_online')
            
            if 'last_seen' in existing_columns:
                conn.execute("ALTER TABLE users DROP COLUMN last_seen")
                dropped_columns.append('last_seen')
            
            conn.commit()
        
        return jsonify({
            'success': True,
            'message': 'Database migration completed',
            'dropped_columns': dropped_columns
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Migration failed: {str(e)}'
        }), 500