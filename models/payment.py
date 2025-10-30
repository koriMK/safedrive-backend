from . import db
from datetime import datetime
import uuid

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