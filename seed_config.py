from models import db, Config, User, Driver
from werkzeug.security import generate_password_hash

def seed_config():
    """Seed configuration data"""
    
    # M-Pesa Configuration
    configs = [
        ('MPESA_CONSUMER_KEY', 'UnDvUCktXcQDyRScx0uAnJlA7rboMWhSnAxvhSOYQiX8QU0t', 'M-Pesa Consumer Key'),
        ('MPESA_CONSUMER_SECRET', 'eP7nwvhM3OwL0nVhRlOCsGnRawPi32BkENmT33NygDpdYdq5sy1WyAshdCnidCkb', 'M-Pesa Consumer Secret'),
        ('MPESA_BUSINESS_SHORTCODE', '174379', 'M-Pesa Business Shortcode'),
        ('MPESA_PASSKEY', 'bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919', 'M-Pesa Passkey'),
        ('MPESA_BASE_URL', 'https://sandbox.safaricom.co.ke', 'M-Pesa Base URL'),
        
        # Trip Configuration
        ('TRIP_BASE_FARE', '200', 'Base fare for trips (KES)'),
        ('TRIP_RATE_PER_KM', '50', 'Rate per kilometer (KES)'),
        ('TRIP_AVERAGE_SPEED', '30', 'Average speed for duration calculation (km/h)'),
        
        # App Configuration
        ('APP_NAME', 'SafeDrive', 'Application name'),
        ('APP_VERSION', '1.0.0', 'Application version'),
        ('SUPPORT_EMAIL', 'support@safedrive.com', 'Support email'),
        ('SUPPORT_PHONE', '+254700000000', 'Support phone number'),
        
        # System Configuration
        ('EARTH_RADIUS_KM', '6371', 'Earth radius for distance calculations'),
        ('MIN_PASSWORD_LENGTH', '8', 'Minimum password length'),
        ('AUTO_COMPLETE_PAYMENT', 'true', 'Auto-complete payment on trip completion'),
        ('ONLINE_TIMEOUT_MINUTES', '5', 'Minutes to consider user offline'),
        ('MPESA_CALLBACK_URL', 'https://safedrive-backend-d579.onrender.com/api/v1/payments/callback', 'M-Pesa callback URL'),
    ]
    
    for key, value, description in configs:
        try:
            existing = Config.query.filter_by(key=key).first()
            if not existing:
                config = Config(key=key, value=value, description=description)
                db.session.add(config)
        except Exception:
            continue
    
    try:
        db.session.commit()
    except Exception:
        db.session.rollback()

def seed_admin_user():
    """Create default admin user"""
    admin_email = 'admin@safedrive.com'
    
    try:
        existing_admin = User.query.filter_by(email=admin_email).first()
        if not existing_admin:
            admin = User(
                email=admin_email,
                name='System Administrator',
                phone=None,
                role='admin'
            )
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
    except Exception:
        db.session.rollback()

def seed_sample_drivers():
    """Create sample approved drivers"""
    sample_drivers = [
        {
            'name': 'John Kamau',
            'email': 'john.kamau@example.com',
            'phone': '+254712345678',
            'vehicle': {
                'make': 'Toyota',
                'model': 'Corolla',
                'year': 2020,
                'plate': 'KCA 123A',
                'color': 'White'
            }
        },
        {
            'name': 'Mary Wanjiku',
            'email': 'mary.wanjiku@example.com', 
            'phone': '+254723456789',
            'vehicle': {
                'make': 'Nissan',
                'model': 'Note',
                'year': 2019,
                'plate': 'KCB 456B',
                'color': 'Silver'
            }
        }
    ]
    
    for driver_data in sample_drivers:
        try:
            existing_user = User.query.filter_by(email=driver_data['email']).first()
            if not existing_user:
                # Create user
                user = User(
                    email=driver_data['email'],
                    name=driver_data['name'],
                    phone=driver_data['phone'],
                    role='driver'
                )
                user.set_password('driver123')
                db.session.add(user)
                db.session.flush()
                
                # Create driver profile
                driver = Driver(
                    user_id=user.id,
                    vehicle_make=driver_data['vehicle']['make'],
                    vehicle_model=driver_data['vehicle']['model'],
                    vehicle_year=driver_data['vehicle']['year'],
                    vehicle_plate=driver_data['vehicle']['plate'],
                    vehicle_color=driver_data['vehicle']['color'],
                    status='approved',
                    is_online=True
                )
                db.session.add(driver)
        except Exception:
            continue
    
    try:
        db.session.commit()
    except Exception:
        db.session.rollback()

def run_seeds():
    """Run all seed functions"""
    try:
        seed_config()
        seed_admin_user()
        seed_sample_drivers()
    except Exception:
        pass