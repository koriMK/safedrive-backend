from . import db
from datetime import datetime
import uuid

class Notification(db.Model):
    __tablename__ = 'notifications'
    
    id = db.Column(db.String(50), primary_key=True, default=lambda: f'notif_{uuid.uuid4().hex[:12]}')
    user_id = db.Column(db.String(50), db.ForeignKey('users.id'), nullable=False, index=True)
    
    # Notification details
    title = db.Column(db.String(255), nullable=False)
    message = db.Column(db.Text, nullable=False)
    type = db.Column(db.String(50), nullable=False, index=True)  # trip_request, payment, system, etc.
    
    # Related entities
    trip_id = db.Column(db.String(50), db.ForeignKey('trips.id'))
    payment_id = db.Column(db.String(50), db.ForeignKey('payments.id'))
    
    # Status
    is_read = db.Column(db.Boolean, default=False, index=True)
    is_sent = db.Column(db.Boolean, default=False)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    read_at = db.Column(db.DateTime)
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'userId': self.user_id,
            'title': self.title,
            'message': self.message,
            'type': self.type,
            'tripId': self.trip_id,
            'paymentId': self.payment_id,
            'isRead': self.is_read,
            'isSent': self.is_sent,
            'createdAt': self.created_at.isoformat(),
            'readAt': self.read_at.isoformat() if self.read_at else None
        }