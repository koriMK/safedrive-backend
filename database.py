import sqlite3
from flask import current_app, g

def get_db():
    """Get database connection"""
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config.get('DATABASE', 'safedrive.db'),
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row
    return g.db

def close_db(e=None):
    """Close database connection"""
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_db():
    """Initialize database tables"""
    db = get_db()
    
    # Create users table
    db.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            name TEXT NOT NULL,
            phone TEXT UNIQUE,
            role TEXT NOT NULL CHECK (role IN ('passenger', 'driver', 'admin')),
            avatar TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create drivers table
    db.execute('''
        CREATE TABLE IF NOT EXISTS drivers (
            id TEXT PRIMARY KEY,
            user_id TEXT UNIQUE NOT NULL,
            vehicle_make TEXT,
            vehicle_model TEXT,
            vehicle_year INTEGER,
            vehicle_plate TEXT UNIQUE,
            vehicle_color TEXT,
            document_id_card TEXT,
            document_license TEXT,
            document_insurance TEXT,
            document_logbook TEXT,
            rating REAL DEFAULT 0.0,
            total_trips INTEGER DEFAULT 0,
            total_earnings REAL DEFAULT 0.0,
            status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'approved', 'suspended')),
            is_online BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            approved_at TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Create trips table
    db.execute('''
        CREATE TABLE IF NOT EXISTS trips (
            id TEXT PRIMARY KEY,
            passenger_id TEXT NOT NULL,
            driver_id TEXT,
            pickup_lat REAL NOT NULL,
            pickup_lng REAL NOT NULL,
            pickup_address TEXT NOT NULL,
            dropoff_lat REAL NOT NULL,
            dropoff_lng REAL NOT NULL,
            dropoff_address TEXT NOT NULL,
            status TEXT DEFAULT 'requested' CHECK (status IN ('requested', 'accepted', 'enroute', 'driving', 'completed', 'cancelled')),
            fare REAL NOT NULL,
            distance REAL NOT NULL,
            duration INTEGER NOT NULL,
            payment_status TEXT DEFAULT 'pending' CHECK (payment_status IN ('pending', 'paid', 'failed')),
            payment_id TEXT,
            rating INTEGER CHECK (rating >= 1 AND rating <= 5),
            feedback TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            accepted_at TIMESTAMP,
            started_at TIMESTAMP,
            completed_at TIMESTAMP,
            cancelled_at TIMESTAMP,
            FOREIGN KEY (passenger_id) REFERENCES users (id),
            FOREIGN KEY (driver_id) REFERENCES users (id)
        )
    ''')
    
    # Create payments table
    db.execute('''
        CREATE TABLE IF NOT EXISTS payments (
            id TEXT PRIMARY KEY,
            trip_id TEXT NOT NULL,
            amount REAL NOT NULL,
            phone TEXT NOT NULL,
            merchant_request_id TEXT,
            checkout_request_id TEXT,
            mpesa_receipt_number TEXT,
            transaction_date TIMESTAMP,
            status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'paid', 'failed')),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (trip_id) REFERENCES trips (id)
        )
    ''')
    
    # Create payouts table
    db.execute('''
        CREATE TABLE IF NOT EXISTS payouts (
            id TEXT PRIMARY KEY,
            driver_id TEXT NOT NULL,
            amount REAL NOT NULL,
            phone TEXT NOT NULL,
            conversation_id TEXT,
            originator_conversation_id TEXT,
            transaction_id TEXT,
            status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'paid', 'failed')),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (driver_id) REFERENCES users (id)
        )
    ''')
    
    # Create notifications table
    db.execute('''
        CREATE TABLE IF NOT EXISTS notifications (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            title TEXT NOT NULL,
            message TEXT NOT NULL,
            type TEXT NOT NULL,
            is_read BOOLEAN DEFAULT 0,
            data TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    db.commit()
    
    # Create admin user if not exists
    admin_check = db.execute('SELECT * FROM users WHERE email = ?', ('admin@safedrive.co.ke',)).fetchone()
    if not admin_check:
        from werkzeug.security import generate_password_hash
        import uuid
        
        admin_id = f'u_{uuid.uuid4().hex[:12]}'
        password_hash = generate_password_hash('admin123')
        
        db.execute('''
            INSERT INTO users (id, email, password_hash, name, phone, role)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (admin_id, 'admin@safedrive.co.ke', password_hash, 'Admin User', '+254700000000', 'admin'))
        db.commit()
        print("Admin user created: admin@safedrive.co.ke / admin123")