from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import uuid

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.String(50), primary_key=True, default=lambda: f'u_{uuid.uuid4().hex[:12]}')
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(20), unique=True, nullable=True, index=True)
    role = db.Column(db.String(20), nullable=False, index=True)  # passenger, driver, admin
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check password against hash"""
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'email': self.email,
            'name': self.name,
            'phone': self.phone,
            'role': self.role,
            'createdAt': self.created_at.isoformat()
        }

class Driver(db.Model):
    __tablename__ = 'drivers'
    
    id = db.Column(db.String(50), primary_key=True, default=lambda: f'd_{uuid.uuid4().hex[:12]}')
    user_id = db.Column(db.String(50), db.ForeignKey('users.id'), unique=True, nullable=False)
    
    # Vehicle
    vehicle_make = db.Column(db.String(100))
    vehicle_model = db.Column(db.String(100))
    vehicle_year = db.Column(db.Integer)
    vehicle_plate = db.Column(db.String(50))
    vehicle_color = db.Column(db.String(50))
    
    # Documents
    document_id_card = db.Column(db.String(500))
    document_license = db.Column(db.String(500))
    document_insurance = db.Column(db.String(500))
    document_logbook = db.Column(db.String(500))
    
    # Stats
    rating = db.Column(db.Numeric(3, 2), default=0.00)
    total_trips = db.Column(db.Integer, default=0)
    total_earnings = db.Column(db.Numeric(10, 2), default=0.00)
    
    # Status
    status = db.Column(db.String(20), default='pending', nullable=False)  # pending, approved, suspended
    is_online = db.Column(db.Boolean, default=False)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    user = db.relationship('User', backref='driver_profile')
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'userId': self.user_id,
            'name': self.user.name if self.user else None,
            'email': self.user.email if self.user else None,
            'phone': self.user.phone if self.user else None,
            'vehicle': {
                'make': self.vehicle_make,
                'model': self.vehicle_model,
                'year': self.vehicle_year,
                'plate': self.vehicle_plate,
                'color': self.vehicle_color
            },
            'documents': {
                'idCard': bool(self.document_id_card),
                'license': bool(self.document_license),
                'insurance': bool(self.document_insurance),
                'logbook': bool(self.document_logbook)
            },
            'rating': float(self.rating) if self.rating else 0,
            'totalTrips': self.total_trips,
            'totalEarnings': float(self.total_earnings) if self.total_earnings else 0,
            'status': self.status,
            'isOnline': self.is_online,
            'createdAt': self.created_at.isoformat()
        }

class Trip(db.Model):
    __tablename__ = 'trips'
    
    id = db.Column(db.String(50), primary_key=True, default=lambda: f't_{uuid.uuid4().hex[:12]}')
    passenger_id = db.Column(db.String(50), db.ForeignKey('users.id'), nullable=False)
    driver_id = db.Column(db.String(50), db.ForeignKey('users.id'))
    
    # Pickup location
    pickup_lat = db.Column(db.Numeric(10, 8), nullable=False)
    pickup_lng = db.Column(db.Numeric(11, 8), nullable=False)
    pickup_address = db.Column(db.String(500), nullable=False)
    
    # Dropoff location
    dropoff_lat = db.Column(db.Numeric(10, 8), nullable=False)
    dropoff_lng = db.Column(db.Numeric(11, 8), nullable=False)
    dropoff_address = db.Column(db.String(500), nullable=False)
    
    # Trip details
    status = db.Column(db.String(20), default='requested', nullable=False)
    fare = db.Column(db.Numeric(10, 2), nullable=False)
    distance = db.Column(db.Numeric(10, 2), nullable=False)  # km
    duration = db.Column(db.Integer, nullable=False)  # minutes
    
    # Payment
    payment_status = db.Column(db.String(20), default='pending', nullable=False)
    
    # Rating
    rating = db.Column(db.Integer)
    feedback = db.Column(db.Text)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    accepted_at = db.Column(db.DateTime)
    started_at = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)
    
    # Relationships
    passenger = db.relationship('User', foreign_keys=[passenger_id])
    driver = db.relationship('User', foreign_keys=[driver_id])
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'passengerId': self.passenger_id,
            'driverId': self.driver_id,
            'pickup': {
                'lat': float(self.pickup_lat),
                'lng': float(self.pickup_lng),
                'address': self.pickup_address
            },
            'dropoff': {
                'lat': float(self.dropoff_lat),
                'lng': float(self.dropoff_lng),
                'address': self.dropoff_address
            },
            'status': self.status,
            'fare': float(self.fare),
            'distance': float(self.distance),
            'duration': self.duration,
            'paymentStatus': self.payment_status,
            'rating': self.rating,
            'feedback': self.feedback,
            'createdAt': self.created_at.isoformat(),
            'acceptedAt': self.accepted_at.isoformat() if self.accepted_at else None,
            'startedAt': self.started_at.isoformat() if self.started_at else None,
            'completedAt': self.completed_at.isoformat() if self.completed_at else None
        }

class Payment(db.Model):
    __tablename__ = 'payments'
    
    id = db.Column(db.String(50), primary_key=True, default=lambda: f'pay_{uuid.uuid4().hex[:12]}')
    trip_id = db.Column(db.String(50), db.ForeignKey('trips.id'), nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    
    # M-Pesa details
    checkout_request_id = db.Column(db.String(100))
    mpesa_receipt_number = db.Column(db.String(100))
    
    # Status
    status = db.Column(db.String(20), default='pending', nullable=False)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'tripId': self.trip_id,
            'amount': float(self.amount),
            'phone': self.phone,
            'checkoutRequestId': self.checkout_request_id,
            'mpesaReceiptNumber': self.mpesa_receipt_number,
            'status': self.status,
            'createdAt': self.created_at.isoformat()
        }