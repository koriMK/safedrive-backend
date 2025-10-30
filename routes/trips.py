from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import Trip, User, Driver, db
from datetime import datetime
import math

trips_bp = Blueprint('trips', __name__)

def calculate_distance(lat1, lon1, lat2, lon2):
    """Calculate distance using Haversine formula"""
    try:
        from models import Config
        R = float(Config.get_value('EARTH_RADIUS_KM', '6371'))
    except:
        R = 6371  # Earth's radius in km
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    return R * c

@trips_bp.route('', methods=['POST'])
@jwt_required()
def create_trip():
    """
    Create new trip request
    ---
    tags:
      - Trips
    security:
      - Bearer: []
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - pickup
            - dropoff
          properties:
            pickup:
              type: object
              properties:
                lat:
                  type: number
                  example: -1.2921
                lng:
                  type: number
                  example: 36.8219
                address:
                  type: string
                  example: "Nairobi CBD"
            dropoff:
              type: object
              properties:
                lat:
                  type: number
                  example: -1.3032
                lng:
                  type: number
                  example: 36.8856
                address:
                  type: string
                  example: "Westlands"
            notifyDrivers:
              type: boolean
              example: true
    responses:
      201:
        description: Trip created successfully
      400:
        description: Validation error
      403:
        description: Unauthorized - Only passengers can request trips
    """
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if user.role != 'passenger':
            return jsonify({
                'success': False,
                'error': {
                    'code': 'UNAUTHORIZED',
                    'message': 'Only passengers can request trips'
                }
            }), 403
        
        data = request.json
        pickup = data.get('pickup')
        dropoff = data.get('dropoff')
        
        if not pickup or not dropoff:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'MISSING_LOCATION',
                    'message': 'Pickup and dropoff locations are required'
                }
            }), 400
        
        # Calculate distance
        distance = calculate_distance(
            float(pickup['lat']), float(pickup['lng']),
            float(dropoff['lat']), float(dropoff['lng'])
        )
        
        # Calculate fare using cached config values
        try:
            from models import Config
            # Cache config values to avoid repeated DB queries
            if not hasattr(create_trip, '_config_cache'):
                create_trip._config_cache = {
                    'BASE_FARE': float(Config.get_value('TRIP_BASE_FARE', '200')),
                    'RATE_PER_KM': float(Config.get_value('TRIP_RATE_PER_KM', '50')),
                    'AVERAGE_SPEED': float(Config.get_value('TRIP_AVERAGE_SPEED', '30'))
                }
            BASE_FARE = create_trip._config_cache['BASE_FARE']
            RATE_PER_KM = create_trip._config_cache['RATE_PER_KM']
            AVERAGE_SPEED = create_trip._config_cache['AVERAGE_SPEED']
        except:
            BASE_FARE = 200
            RATE_PER_KM = 50
            AVERAGE_SPEED = 30
        
        fare = BASE_FARE + (distance * RATE_PER_KM)
        duration = int((distance / AVERAGE_SPEED) * 60)  # minutes
        
        # Create trip
        trip = Trip(
            passenger_id=user_id,
            pickup_lat=pickup['lat'],
            pickup_lng=pickup['lng'],
            pickup_address=pickup['address'],
            dropoff_lat=dropoff['lat'],
            dropoff_lng=dropoff['lng'],
            dropoff_address=dropoff['address'],
            fare=round(fare, 2),
            distance=round(distance, 2),
            duration=duration,
            status='requested'
        )
        
        db.session.add(trip)
        db.session.commit()
        
        # If notifyDrivers flag is set, find nearby online drivers
        if data.get('notifyDrivers'):
            online_drivers = Driver.query.filter_by(is_online=True, status='approved').all()
        
        return jsonify({
            'success': True,
            'message': 'Trip requested successfully',
            'data': trip.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': {
                'code': 'TRIP_CREATE_FAILED',
                'message': str(e)
            }
        }), 500

@trips_bp.route('', methods=['GET'])
@jwt_required()
def get_trips():
    """
    Get user's trips
    ---
    tags:
      - Trips
    security:
      - Bearer: []
    parameters:
      - name: page
        in: query
        type: integer
        default: 1
        description: Page number
      - name: limit
        in: query
        type: integer
        default: 10
        description: Items per page
      - name: status
        in: query
        type: string
        enum: ["requested", "accepted", "driving", "completed", "cancelled"]
        description: Filter by trip status
    responses:
      200:
        description: Trips retrieved successfully
      500:
        description: Server error
    """
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', 10, type=int)
        status = request.args.get('status')
        
        # Build query based on user role
        if user.role == 'passenger':
            query = Trip.query.filter_by(passenger_id=user_id)
        elif user.role == 'driver':
            query = Trip.query.filter_by(driver_id=user_id)
        else:  # admin
            query = Trip.query
        
        if status:
            query = query.filter_by(status=status)
        
        # Get trips with eager loading for better performance
        trips = query.options(
            db.joinedload(Trip.passenger),
            db.joinedload(Trip.driver)
        ).order_by(Trip.created_at.desc()).limit(limit).offset((page-1)*limit).all()
        total = query.count()
        
        return jsonify({
            'success': True,
            'data': {
                'trips': [trip.to_dict() for trip in trips],
                'pagination': {
                    'page': page,
                    'limit': limit,
                    'total': total,
                    'pages': math.ceil(total / limit)
                }
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

@trips_bp.route('/<trip_id>/accept', methods=['PUT'])
@jwt_required()
def accept_trip(trip_id):
    """
    Driver accepts trip
    ---
    tags:
      - Trips
    security:
      - Bearer: []
    parameters:
      - name: trip_id
        in: path
        type: string
        required: true
        description: Trip ID
    responses:
      200:
        description: Trip accepted successfully
      400:
        description: Trip not available
      403:
        description: Unauthorized - Only drivers can accept trips
      404:
        description: Trip not found
    """
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if user.role != 'driver':
            return jsonify({
                'success': False,
                'error': {
                    'code': 'UNAUTHORIZED',
                    'message': 'Only drivers can accept trips'
                }
            }), 403
        
        trip = Trip.query.get(trip_id)
        
        if not trip:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'TRIP_NOT_FOUND',
                    'message': 'Trip not found'
                }
            }), 404
        
        if trip.status != 'requested':
            return jsonify({
                'success': False,
                'error': {
                    'code': 'INVALID_STATUS',
                    'message': 'Trip is not available'
                }
            }), 400
        
        # Update trip
        trip.driver_id = user_id
        trip.status = 'accepted'
        trip.accepted_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Trip accepted',
            'data': trip.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': {
                'code': 'ACCEPT_FAILED',
                'message': str(e)
            }
        }), 500

@trips_bp.route('/<trip_id>/complete', methods=['PUT'])
@jwt_required()
def complete_trip(trip_id):
    """
    Complete trip
    ---
    tags:
      - Trips
    security:
      - Bearer: []
    parameters:
      - name: trip_id
        in: path
        type: string
        required: true
        description: Trip ID
    responses:
      200:
        description: Trip completed successfully
      403:
        description: Unauthorized
      404:
        description: Trip not found
    """
    try:
        user_id = get_jwt_identity()
        trip = Trip.query.get(trip_id)
        
        if not trip or trip.driver_id != user_id:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'UNAUTHORIZED',
                    'message': 'Unauthorized'
                }
            }), 403
        
        trip.status = 'completed'
        trip.completed_at = datetime.utcnow()
        # Update payment status based on config
        try:
            from models import Config
            auto_payment = Config.get_value('AUTO_COMPLETE_PAYMENT', 'true').lower() == 'true'
            trip.payment_status = 'paid' if auto_payment else 'pending'
        except:
            trip.payment_status = 'paid'  # Default behavior
        
        # Update driver stats
        driver = Driver.query.filter_by(user_id=user_id).first()
        if driver:
            driver.total_trips += 1
            driver.total_earnings += trip.fare
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Trip completed',
            'data': trip.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': {
                'code': 'COMPLETE_FAILED',
                'message': str(e)
            }
        }), 500

@trips_bp.route('/<trip_id>/rate', methods=['POST'])
@jwt_required()
def rate_trip(trip_id):
    """
    Rate completed trip
    ---
    tags:
      - Trips
    security:
      - Bearer: []
    parameters:
      - name: trip_id
        in: path
        type: string
        required: true
        description: Trip ID
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - rating
          properties:
            rating:
              type: integer
              minimum: 1
              maximum: 5
              example: 5
            feedback:
              type: string
              example: "Great driver, smooth ride!"
    responses:
      200:
        description: Rating submitted successfully
      400:
        description: Invalid rating value
      403:
        description: Unauthorized
    """
    try:
        user_id = get_jwt_identity()
        trip = Trip.query.get(trip_id)
        
        if not trip or trip.passenger_id != user_id:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'UNAUTHORIZED',
                    'message': 'Unauthorized'
                }
            }), 403
        
        data = request.json
        rating = data.get('rating')
        feedback = data.get('feedback', '')
        
        if not rating or rating < 1 or rating > 5:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'INVALID_RATING',
                    'message': 'Rating must be between 1 and 5'
                }
            }), 400
        
        trip.rating = rating
        trip.feedback = feedback
        
        # Update driver rating
        if trip.driver_id:
            driver = Driver.query.filter_by(user_id=trip.driver_id).first()
            if driver:
                # Calculate new average rating efficiently
                avg_rating = db.session.query(db.func.avg(Trip.rating)).filter(
                    Trip.driver_id == trip.driver_id,
                    Trip.rating.isnot(None)
                ).scalar()
                
                driver.rating = round(float(avg_rating), 2) if avg_rating else 0
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Rating submitted',
            'data': trip.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': {
                'code': 'RATING_FAILED',
                'message': str(e)
            }
        }), 500

@trips_bp.route('/available', methods=['GET'])
@jwt_required()
def get_available_trips():
    """
    Get available trips for drivers
    ---
    tags:
      - Trips
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
        
        # Get trips that are requested and not assigned with optimization
        trips = Trip.query.options(
            db.joinedload(Trip.passenger)
        ).filter_by(status='requested', driver_id=None).order_by(Trip.created_at.desc()).limit(20).all()
        
        return jsonify({
            'success': True,
            'data': [trip.to_dict() for trip in trips]
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'FETCH_FAILED',
                'message': str(e)
            }
        }), 500

@trips_bp.route('/<trip_id>', methods=['GET'])
@jwt_required()
def get_trip(trip_id):
    """
    Get specific trip
    ---
    tags:
      - Trips
    security:
      - Bearer: []
    parameters:
      - name: trip_id
        in: path
        type: string
        required: true
        description: Trip ID
    responses:
      200:
        description: Trip retrieved successfully
      404:
        description: Trip not found
    """
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        trip = Trip.query.get(trip_id)
        if not trip:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'NOT_FOUND',
                    'message': 'Trip not found'
                }
            }), 404
        
        # Check authorization
        if user.role not in ['admin'] and trip.passenger_id != user_id and trip.driver_id != user_id:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'UNAUTHORIZED',
                    'message': 'Unauthorized to view this trip'
                }
            }), 403
        
        return jsonify({
            'success': True,
            'data': trip.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'FETCH_FAILED',
                'message': str(e)
            }
        }), 500

@trips_bp.route('/<trip_id>', methods=['PUT'])
@jwt_required()
def update_trip(trip_id):
    """
    Update trip
    ---
    tags:
      - Trips
    security:
      - Bearer: []
    parameters:
      - name: trip_id
        in: path
        type: string
        required: true
        description: Trip ID
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            status:
              type: string
              enum: ["requested", "accepted", "driving", "completed", "cancelled"]
              example: "driving"
    responses:
      200:
        description: Trip updated successfully
      404:
        description: Trip not found
    """
    try:
        user_id = get_jwt_identity()
        trip = Trip.query.get(trip_id)
        
        if not trip:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'NOT_FOUND',
                    'message': 'Trip not found'
                }
            }), 404
        
        # Only driver can update trip status
        if trip.driver_id != user_id:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'UNAUTHORIZED',
                    'message': 'Only assigned driver can update trip'
                }
            }), 403
        
        data = request.json
        if 'status' in data:
            trip.status = data['status']
            if data['status'] == 'driving':
                trip.started_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Trip updated',
            'data': trip.to_dict()
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

@trips_bp.route('/<trip_id>', methods=['DELETE'])
@jwt_required()
def delete_trip(trip_id):
    """
    Delete trip (cancel)
    ---
    tags:
      - Trips
    security:
      - Bearer: []
    parameters:
      - name: trip_id
        in: path
        type: string
        required: true
        description: Trip ID
    responses:
      200:
        description: Trip cancelled successfully
      404:
        description: Trip not found
    """
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        trip = Trip.query.get(trip_id)
        
        if not trip:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'NOT_FOUND',
                    'message': 'Trip not found'
                }
            }), 404
        
        # Only passenger, assigned driver, or admin can cancel
        if user.role != 'admin' and trip.passenger_id != user_id and trip.driver_id != user_id:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'UNAUTHORIZED',
                    'message': 'Unauthorized to cancel this trip'
                }
            }), 403
        
        # Can only cancel if not completed
        if trip.status == 'completed':
            return jsonify({
                'success': False,
                'error': {
                    'code': 'INVALID_STATUS',
                    'message': 'Cannot cancel completed trip'
                }
            }), 400
        
        trip.status = 'cancelled'
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Trip cancelled'
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