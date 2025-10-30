#!/usr/bin/env python3
"""Test payment functionality"""

from app import create_app
from models import db, User, Trip, Payment
from services.mpesa import MpesaService

def test_payment():
    app = create_app()
    with app.app_context():
        print("🧪 Testing Payment System...")
        
        # Test M-Pesa service initialization
        try:
            mpesa = MpesaService()
            print("✅ M-Pesa service initialized")
        except Exception as e:
            print(f"❌ M-Pesa service error: {e}")
            return
        
        # Test access token
        try:
            token = mpesa.get_access_token()
            if token:
                print("✅ M-Pesa access token obtained")
            else:
                print("❌ Failed to get M-Pesa access token")
        except Exception as e:
            print(f"❌ Access token error: {e}")
        
        # Test database models
        try:
            payment_count = Payment.query.count()
            trip_count = Trip.query.count()
            print(f"✅ Database accessible - {payment_count} payments, {trip_count} trips")
        except Exception as e:
            print(f"❌ Database error: {e}")
        
        print("🎉 Payment system test completed!")

if __name__ == '__main__':
    test_payment()