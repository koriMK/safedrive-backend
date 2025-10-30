from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import Driver, User, Trip
from models import db
from datetime import datetime, timedelta
import os
from werkzeug.utils import secure_filename
import uuid

drivers_bp = Blueprint('drivers', __name__)

UPLOAD_FOLDER = 'uploads/documents'
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@drivers_bp.route('/available-trips', methods=['GET'])
@jwt_required()
def get_available_trips():
    """
    Get available trips for driver
    ---
    tags:
      - Drivers
    security:
      - Bearer: []
    responses:
      200:
        description: Available trips retrieved successfully
      403:
        description: Unauthorized - Only drivers can view available trips
    """
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if user.role != 'driver':
            return jsonify({
                'success': False,
                'error': {
                    'code': 'UNAUTHORIZED',
                    'message': 'Only drivers can view available trips'
                }
            }), 403
        
        # Get trips with status 'requested' with optimization
        trips = Trip.query.options(
            db.joinedload(Trip.passenger)
        ).filter_by(status='requested').order_by(Trip.created_at.desc()).limit(20).all()
        
        return jsonify({
            'success': True,
            'data': {
                'trips': [trip.to_dict() for trip in trips]
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

@drivers_bp.route('/status', methods=['PUT'])
@jwt_required()
def update_driver_status():
    """
    Update driver online status
    ---
    tags:
      - Drivers
    security:
      - Bearer: []
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - isOnline
          properties:
            isOnline:
              type: boolean
              example: true
    responses:
      200:
        description: Status updated successfully
      400:
        description: Missing required field
      403:
        description: Unauthorized - Only drivers can update status
    """
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if user.role != 'driver':
            return jsonify({
                'success': False,
                'error': {
                    'code': 'UNAUTHORIZED',
                    'message': 'Only drivers can update status'
                }
            }), 403
        
        data = request.json
        is_online = data.get('isOnline')
        
        if is_online is None:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'MISSING_FIELD',
                    'message': 'isOnline field is required'
                }
            }), 400
        
        driver = Driver.query.filter_by(user_id=user_id).first()
        
        if not driver:
            # Create driver profile if it doesn't exist
            driver = Driver(user_id=user_id, status='approved')  # Auto-approve for demo
            db.session.add(driver)
        
        driver.is_online = is_online
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Status updated',
            'data': {
                'isOnline': driver.is_online
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': {
                'code': 'UPDATE_FAILED',
                'message': str(e)
            }
        }), 500

@drivers_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_driver_profile():
    """
    Get driver profile
    ---
    tags:
      - Drivers
    security:
      - Bearer: []
    responses:
      200:
        description: Driver profile retrieved successfully
      403:
        description: Unauthorized - Only drivers can access this endpoint
    """
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if user.role != 'driver':
            return jsonify({
                'success': False,
                'error': {
                    'code': 'UNAUTHORIZED',
                    'message': 'Only drivers can access this endpoint'
                }
            }), 403
        
        driver = Driver.query.filter_by(user_id=user_id).first()
        
        if not driver:
            # Create driver profile if it doesn't exist
            driver = Driver(user_id=user_id)
            db.session.add(driver)
            db.session.commit()
        
        return jsonify({
            'success': True,
            'data': driver.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'FETCH_FAILED',
                'message': str(e)
            }
        }), 500

@drivers_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_driver_profile():
    """
    Update driver profile
    ---
    tags:
      - Drivers
    security:
      - Bearer: []
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            vehicle:
              type: object
              properties:
                make:
                  type: string
                  example: "Toyota"
                model:
                  type: string
                  example: "Corolla"
                year:
                  type: integer
                  example: 2020
                plate:
                  type: string
                  example: "KCA 123A"
                color:
                  type: string
                  example: "White"
    responses:
      200:
        description: Profile updated successfully
      403:
        description: Unauthorized - Only drivers can update profile
    """
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if user.role != 'driver':
            return jsonify({
                'success': False,
                'error': {
                    'code': 'UNAUTHORIZED',
                    'message': 'Only drivers can update profile'
                }
            }), 403
        
        data = request.json
        vehicle = data.get('vehicle', {})
        
        # Get or create driver profile
        driver = Driver.query.filter_by(user_id=user_id).first()
        if not driver:
            driver = Driver(user_id=user_id)
            db.session.add(driver)
        
        # Update vehicle information with validation
        if vehicle:
            # Sanitize and validate inputs
            make = str(vehicle.get('make', driver.vehicle_make or ''))[:100]
            model = str(vehicle.get('model', driver.vehicle_model or ''))[:100]
            plate = str(vehicle.get('plate', driver.vehicle_plate or ''))[:20]
            color = str(vehicle.get('color', driver.vehicle_color or ''))[:50]
            
            driver.vehicle_make = make.strip() if make else driver.vehicle_make
            driver.vehicle_model = model.strip() if model else driver.vehicle_model
            driver.vehicle_year = vehicle.get('year', driver.vehicle_year)
            driver.vehicle_plate = plate.strip().upper() if plate else driver.vehicle_plate
            driver.vehicle_color = color.strip() if color else driver.vehicle_color
        
        driver.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Profile updated successfully',
            'data': driver.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': {
                'code': 'UPDATE_FAILED',
                'message': str(e)
            }
        }), 500

@drivers_bp.route('/upload-document', methods=['POST'])
@jwt_required()
def upload_document():
    """
    Upload driver document
    ---
    tags:
      - Drivers
    security:
      - Bearer: []
    consumes:
      - multipart/form-data
    parameters:
      - name: file
        in: formData
        type: file
        required: true
        description: Document file (PDF, PNG, JPG, JPEG)
      - name: type
        in: formData
        type: string
        required: true
        enum: ["idCard", "license", "insurance", "logbook"]
        description: Document type
    responses:
      200:
        description: Document uploaded successfully
      400:
        description: Invalid file or missing parameters
      403:
        description: Unauthorized - Only drivers can upload documents
    """
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if user.role != 'driver':
            return jsonify({
                'success': False,
                'error': {
                    'code': 'UNAUTHORIZED',
                    'message': 'Only drivers can upload documents'
                }
            }), 403
        
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'NO_FILE',
                    'message': 'No file provided'
                }
            }), 400
        
        file = request.files['file']
        document_type = request.form.get('type')  # idCard, license, insurance, logbook
        
        if not document_type or document_type not in ['idCard', 'license', 'insurance', 'logbook']:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'INVALID_TYPE',
                    'message': 'Invalid document type'
                }
            }), 400
        
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': {
                    'code': 'NO_FILE',
                    'message': 'No file selected'
                }
            }), 400
        
        if file and allowed_file(file.filename):
            try:
                # Create upload directory if it doesn't exist
                os.makedirs(UPLOAD_FOLDER, exist_ok=True)
                
                # Validate file size (max 5MB)
                file.seek(0, os.SEEK_END)
                file_size = file.tell()
                file.seek(0)
                
                if file_size > 5 * 1024 * 1024:  # 5MB limit
                    return jsonify({
                        'success': False,
                        'error': {
                            'code': 'FILE_TOO_LARGE',
                            'message': 'File size must be less than 5MB'
                        }
                    }), 400
                
                # Generate secure unique filename
                ext = file.filename.rsplit('.', 1)[1].lower()
                filename = f"{user_id}_{document_type}_{uuid.uuid4().hex[:8]}.{ext}"
                filepath = os.path.join(UPLOAD_FOLDER, filename)
                
                # Validate file path is within upload directory
                abs_upload_path = os.path.abspath(UPLOAD_FOLDER)
                abs_file_path = os.path.abspath(filepath)
                if not abs_file_path.startswith(abs_upload_path):
                    return jsonify({
                        'success': False,
                        'error': {
                            'code': 'INVALID_PATH',
                            'message': 'Invalid file path'
                        }
                    }), 400
                
                # Save file
                file.save(filepath)
                
                # Verify file was saved successfully
                if not os.path.exists(filepath):
                    return jsonify({
                        'success': False,
                        'error': {
                            'code': 'SAVE_FAILED',
                            'message': 'Failed to save file'
                        }
                    }), 500
                    
            except Exception as save_error:
                return jsonify({
                    'success': False,
                    'error': {
                        'code': 'SAVE_ERROR',
                        'message': f'File save error: {str(save_error)}'
                    }
                }), 500
            
            # Update driver profile
            driver = Driver.query.filter_by(user_id=user_id).first()
            if not driver:
                driver = Driver(user_id=user_id)
                db.session.add(driver)
            
            if document_type == 'idCard':
                driver.document_id_card = filepath
            elif document_type == 'license':
                driver.document_license = filepath
            elif document_type == 'insurance':
                driver.document_insurance = filepath
            elif document_type == 'logbook':
                driver.document_logbook = filepath
            
            # Check if all required documents are uploaded
            if (driver.document_id_card and driver.document_license and 
                driver.vehicle_make and driver.vehicle_plate):
                driver.status = 'pending'  # Ready for admin review
            
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': 'Document uploaded successfully',
                'data': {
                    'type': document_type,
                    'uploaded': True
                }
            }), 200
        
        return jsonify({
            'success': False,
            'error': {
                'code': 'INVALID_FILE',
                'message': 'Invalid file type. Allowed: pdf, png, jpg, jpeg'
            }
        }), 400
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'UPLOAD_FAILED',
                'message': str(e)
            }
        }), 500

@drivers_bp.route('/earnings', methods=['GET'])
@jwt_required()
def get_driver_earnings():
    """
    Get driver earnings summary
    ---
    tags:
      - Drivers
    security:
      - Bearer: []
    responses:
      200:
        description: Earnings retrieved successfully
      403:
        description: Unauthorized - Only drivers can view earnings
    """
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if user.role != 'driver':
            return jsonify({
                'success': False,
                'error': {
                    'code': 'UNAUTHORIZED',
                    'message': 'Only drivers can view earnings'
                }
            }), 403
        
        # Get completed trips
        completed_trips = Trip.query.filter_by(
            driver_id=user_id,
            status='completed'
        ).all()
        
        # Calculate earnings
        total_earnings = sum(float(trip.fare) for trip in completed_trips)
        total_trips = len(completed_trips)
        
        # Get today's earnings
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        today_trips = [t for t in completed_trips if t.completed_at and t.completed_at >= today_start]
        today_earnings = sum(float(trip.fare) for trip in today_trips)
        
        # Get this week's earnings
        week_start = datetime.utcnow() - timedelta(days=datetime.utcnow().weekday())
        week_start = week_start.replace(hour=0, minute=0, second=0, microsecond=0)
        week_trips = [t for t in completed_trips if t.completed_at and t.completed_at >= week_start]
        week_earnings = sum(float(trip.fare) for trip in week_trips)
        
        # Get driver rating
        driver = Driver.query.filter_by(user_id=user_id).first()
        rating = float(driver.rating) if driver and driver.rating else 0
        
        return jsonify({
            'success': True,
            'data': {
                'totalEarnings': total_earnings,
                'totalTrips': total_trips,
                'todayEarnings': today_earnings,
                'todayTrips': len(today_trips),
                'weekEarnings': week_earnings,
                'weekTrips': len(week_trips),
                'averagePerTrip': total_earnings / total_trips if total_trips > 0 else 0,
                'rating': rating
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

@drivers_bp.route('/payout', methods=['POST'])
@jwt_required()
def request_payout():
    """
    Request driver payout
    ---
    tags:
      - Drivers
    security:
      - Bearer: []
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - amount
            - phone
          properties:
            amount:
              type: number
              example: 1000
            phone:
              type: string
              example: "+254712345678"
    responses:
      200:
        description: Payout request submitted successfully
      400:
        description: Missing required fields
      403:
        description: Unauthorized - Only drivers can request payouts
    """
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if user.role != 'driver':
            return jsonify({
                'success': False,
                'error': {
                    'code': 'UNAUTHORIZED',
                    'message': 'Only drivers can request payouts'
                }
            }), 403
        
        data = request.json
        amount = data.get('amount')
        phone = data.get('phone')
        
        if not amount or not phone:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'MISSING_FIELDS',
                    'message': 'Amount and phone number are required'
                }
            }), 400
        
        # Mock payout processing
        payout_id = f'po_{uuid.uuid4().hex[:12]}'
        
        return jsonify({
            'success': True,
            'message': 'Payout request submitted successfully',
            'data': {
                'payoutId': payout_id,
                'amount': amount,
                'phone': phone,
                'status': 'processing'
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'PAYOUT_FAILED',
                'message': str(e)
            }
        }), 500

@drivers_bp.route('/<driver_id>', methods=['GET'])
@jwt_required()
def get_driver(driver_id):
    """
    Get specific driver (admin only)
    ---
    tags:
      - Drivers
    security:
      - Bearer: []
    parameters:
      - name: driver_id
        in: path
        type: string
        required: true
        description: Driver ID
    responses:
      200:
        description: Driver retrieved successfully
      403:
        description: Admin access required
      404:
        description: Driver not found
    """
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        if current_user.role != 'admin':
            return jsonify({
                'success': False,
                'error': {
                    'code': 'ADMIN_REQUIRED',
                    'message': 'Admin access required'
                }
            }), 403
        
        driver = Driver.query.get(driver_id)
        if not driver:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'NOT_FOUND',
                    'message': 'Driver not found'
                }
            }), 404
        
        return jsonify({
            'success': True,
            'data': driver.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'FETCH_FAILED',
                'message': str(e)
            }
        }), 500

@drivers_bp.route('/<driver_id>', methods=['DELETE'])
@jwt_required()
def delete_driver(driver_id):
    """
    Delete driver (admin only)
    ---
    tags:
      - Drivers
    security:
      - Bearer: []
    parameters:
      - name: driver_id
        in: path
        type: string
        required: true
        description: Driver ID
    responses:
      200:
        description: Driver deleted successfully
      403:
        description: Admin access required
      404:
        description: Driver not found
    """
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        if current_user.role != 'admin':
            return jsonify({
                'success': False,
                'error': {
                    'code': 'ADMIN_REQUIRED',
                    'message': 'Admin access required'
                }
            }), 403
        
        driver = Driver.query.get(driver_id)
        if not driver:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'NOT_FOUND',
                    'message': 'Driver not found'
                }
            }), 404
        
        db.session.delete(driver)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Driver deleted'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': {
                'code': 'DELETE_FAILED',
                'message': str(e)
            }
        }), 500

@drivers_bp.route('/<driver_id>/stats', methods=['GET'])
@jwt_required()
def get_driver_stats(driver_id):
    """
    Get driver statistics
    ---
    tags:
      - Drivers
    security:
      - Bearer: []
    parameters:
      - name: driver_id
        in: path
        type: string
        required: true
        description: Driver ID
    responses:
      200:
        description: Driver statistics retrieved successfully
      403:
        description: Admin access required
      404:
        description: Driver not found
    """
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        if current_user.role != 'admin':
            return jsonify({
                'success': False,
                'error': {
                    'code': 'ADMIN_REQUIRED',
                    'message': 'Admin access required'
                }
            }), 403
        
        driver = Driver.query.get(driver_id)
        if not driver:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'NOT_FOUND',
                    'message': 'Driver not found'
                }
            }), 404
        
        # Get today's stats
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        today_trips = Trip.query.filter(
            Trip.driver_id == driver.user_id,
            Trip.status == 'completed',
            Trip.completed_at >= today_start
        ).all()
        
        today_earnings = sum(float(trip.fare) for trip in today_trips)
        today_trips_count = len(today_trips)
        
        return jsonify({
            'success': True,
            'data': {
                'todayEarnings': today_earnings,
                'todayTrips': today_trips_count,
                'totalTrips': driver.total_trips,
                'rating': float(driver.rating) if driver.rating else 0
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'STATS_FAILED',
                'message': str(e)
            }
        }), 500