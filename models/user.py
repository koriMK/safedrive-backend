from . import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import uuid

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.String(50), primary_key=True, default=lambda: f'u_{uuid.uuid4().hex[:12]}')
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(255), nullable=False, index=True)  # Add index for search
    phone = db.Column(db.String(20), unique=True, nullable=True, index=True)
    role = db.Column(db.String(20), nullable=False, index=True)  # passenger, driver, admin
    
    # Profile fields
    profile_picture = db.Column(db.String(500))  # Profile image path
    date_of_birth = db.Column(db.Date)
    gender = db.Column(db.String(10))  # male, female, other
    
    # Location
    current_lat = db.Column(db.Numeric(10, 8))
    current_lng = db.Column(db.Numeric(11, 8))
    
    # Status
    is_active = db.Column(db.Boolean, default=True)
    email_verified = db.Column(db.Boolean, default=False)
    phone_verified = db.Column(db.Boolean, default=False)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)  # Add index for sorting
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
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
            'profilePicture': self.profile_picture,
            'dateOfBirth': self.date_of_birth.isoformat() if self.date_of_birth else None,
            'gender': self.gender,
            'currentLocation': {
                'lat': float(self.current_lat) if self.current_lat else None,
                'lng': float(self.current_lng) if self.current_lng else None
            } if self.current_lat and self.current_lng else None,
            'isActive': self.is_active,
            'emailVerified': self.email_verified,
            'phoneVerified': self.phone_verified,
            'createdAt': self.created_at.isoformat(),
            'updatedAt': self.updated_at.isoformat()
        }