from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import Payment, Trip
from models import db
import uuid
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from services.mpesa import MpesaService

payments_bp = Blueprint('payments', __name__)

@payments_bp.route('/callback', methods=['POST'])
def mpesa_callback():
    """Handle M-Pesa callback"""
    try:
        data = request.json
        checkout_request_id = data.get('Body', {}).get('stkCallback', {}).get('CheckoutRequestID')
        result_code = data.get('Body', {}).get('stkCallback', {}).get('ResultCode')
        
        if checkout_request_id:
            payment = Payment.query.filter_by(checkout_request_id=checkout_request_id).first()
            
            if payment:
                if result_code == 0:  # Success
                    payment.status = 'paid'
                    callback_metadata = data.get('Body', {}).get('stkCallback', {}).get('CallbackMetadata', {}).get('Item', [])
                    
                    for item in callback_metadata:
                        if item.get('Name') == 'MpesaReceiptNumber':
                            payment.mpesa_receipt_number = item.get('Value')
                    
                    # Update trip payment status
                    trip = Trip.query.get(payment.trip_id)
                    if trip:
                        trip.payment_status = 'paid'
                else:
                    payment.status = 'failed'
                
                db.session.commit()
        
        return jsonify({'ResultCode': 0, 'ResultDesc': 'Success'}), 200
        
    except Exception as e:
        print(f'Callback error: {str(e)}')
        return jsonify({'ResultCode': 1, 'ResultDesc': 'Failed'}), 500

@payments_bp.route('/initiate', methods=['POST'])
@jwt_required()
def initiate_payment():
    """Initiate M-Pesa payment"""
    try:
        user_id = get_jwt_identity()
        data = request.json
        
        trip_id = data.get('tripId')
        phone = data.get('phone')
        amount = data.get('amount')
        
        if not all([trip_id, phone, amount]):
            return jsonify({
                'success': False,
                'error': {
                    'code': 'MISSING_FIELDS',
                    'message': 'Trip ID, phone, and amount are required'
                }
            }), 400
        
        # Verify trip exists and belongs to user
        trip = Trip.query.get(trip_id)
        if not trip or trip.passenger_id != user_id:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'TRIP_NOT_FOUND',
                    'message': 'Trip not found or unauthorized'
                }
            }), 404
        
        # Initialize M-Pesa service and initiate STK Push
        mpesa = MpesaService()
        print(f"Initiating payment for trip {trip_id}, amount {amount}, phone {phone}")
        
        stk_result = mpesa.stk_push(
            phone_number=phone,
            amount=amount,
            account_reference=f'Trip{trip_id}',
            transaction_desc=f'Payment for trip'
        )
        
        print(f"STK Push result: {stk_result}")
        
        if not stk_result.get('success'):
            error_msg = stk_result.get('error', 'Unknown M-Pesa error')
            print(f"M-Pesa error: {error_msg}")
            return jsonify({
                'success': False,
                'error': {
                    'code': 'MPESA_FAILED',
                    'message': f'M-Pesa payment failed: {error_msg}'
                }
            }), 400
        
        # Create payment record
        payment = Payment(
            trip_id=trip_id,
            amount=amount,
            phone=phone,
            checkout_request_id=stk_result.get('checkout_request_id'),
            status='pending'
        )
        
        db.session.add(payment)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'STK Push sent to your phone',
            'data': {
                'paymentId': payment.id,
                'checkoutRequestId': payment.checkout_request_id,
                'status': 'pending',
                'responseDescription': stk_result.get('response_description')
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': {
                'code': 'PAYMENT_FAILED',
                'message': str(e)
            }
        }), 500

@payments_bp.route('/status/<payment_id>', methods=['GET'])
@jwt_required()
def check_payment_status(payment_id):
    """Check payment status"""
    try:
        payment = Payment.query.get(payment_id)
        
        if not payment:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'PAYMENT_NOT_FOUND',
                    'message': 'Payment not found'
                }
            }), 404
        
        # Query actual M-Pesa payment status
        if payment.status == 'pending' and payment.checkout_request_id:
            mpesa = MpesaService()
            status_result = mpesa.query_stk_status(payment.checkout_request_id)
            
            if status_result['success']:
                status_data = status_result['data']
                result_code = status_data.get('ResultCode')
                
                if result_code == '0':  # Success
                    payment.status = 'paid'
                    payment.mpesa_receipt_number = status_data.get('MpesaReceiptNumber', f'MPE{uuid.uuid4().hex[:8].upper()}')
                    
                    # Update trip payment status
                    trip = Trip.query.get(payment.trip_id)
                    if trip:
                        trip.payment_status = 'paid'
                    
                    db.session.commit()
                elif result_code in ['1032', '1037']:  # Cancelled or timeout
                    payment.status = 'failed'
                    db.session.commit()
        
        return jsonify({
            'success': True,
            'data': payment.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'STATUS_CHECK_FAILED',
                'message': str(e)
            }
        }), 500

@payments_bp.route('', methods=['GET'])
@jwt_required()
def get_payments():
    """Get user payments"""
    try:
        user_id = get_jwt_identity()
        
        # Get payments for user's trips
        payments = db.session.query(Payment).join(Trip).filter(
            Trip.passenger_id == user_id
        ).order_by(Payment.created_at.desc()).all()
        
        return jsonify({
            'success': True,
            'data': {
                'payments': [payment.to_dict() for payment in payments]
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'FETCH_FAILED',
                'message': str(e)
            }
        }), 500