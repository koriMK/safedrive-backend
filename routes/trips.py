# SafeDrive Backend - Trip Management Routes
# 
# This module handles all trip-related operations for the ride-sharing platform:
# 
# Core Features:
# - Trip creation with fare calculation using Haversine distance formula
# - Driver trip acceptance and status management
# - Trip completion with automatic payment processing
# - Trip rating and feedback system
# - Available trips discovery for drivers
# - Complete CRUD operations with proper authorization
# 
# Security Features:
# - JWT authentication required for all endpoints
# - Role-based access control (passenger, driver, admin)
# - Data access restrictions based on user relationships
# 
# Performance Optimizations:
# - Database query optimization with eager loading
# - Configuration value caching to reduce DB queries
# - Pagination support for large datasets
# 
# Business Logic:
# - Dynamic fare calculation based on distance and configurable rates
# - Driver performance tracking (trips completed, earnings, ratings)
# - Trip lifecycle management (requested → accepted → driving → completed)
# - Automatic driver rating updates based on passenger feedback

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import Trip, User, Driver, db
from datetime import datetime
import math

# Initialize trips blueprint for modular route organization
trips_bp = Blueprint('trips', __name__)

def calculate_distance(lat1, lon1, lat2, lon2):
    """
    Calculate distance between two geographic points using Haversine formula
    
    Args:
        lat1, lon1: Latitude and longitude of first point (pickup)
        lat2, lon2: Latitude and longitude of second point (dropoff)
    
    Returns:
        float: Distance in kilometers
    
    Note:
        Uses Earth's radius from config or defaults to 6371 km
    """
    try:
        # Try to get Earth's radius from dynamic config
        from models import Config
        R = float(Config.get_value('EARTH_RADIUS_KM', '6371'))
    except:
        # Fallback to standard Earth radius in kilometers
        R = 6371
    
    # Convert latitude and longitude differences to radians
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    
    # Haversine formula calculation
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    
    # Return distance in kilometers
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
        
        # Calculate trip distance using Haversine formula
        distance = calculate_distance(
            float(pickup['lat']), float(pickup['lng']),
            float(dropoff['lat']), float(dropoff['lng'])
        )
        
        # Calculate fare using cached config values for performance
        try:
            from models import Config
            # Cache config values to avoid repeated database queries on each trip creation
            if not hasattr(create_trip, '_config_cache'):
                create_trip._config_cache = {
                    'BASE_FARE': float(Config.get_value('TRIP_BASE_FARE', '200')),      # Base fare in KES
                    'RATE_PER_KM': float(Config.get_value('TRIP_RATE_PER_KM', '50')),   # Rate per kilometer
                    'AVERAGE_SPEED': float(Config.get_value('TRIP_AVERAGE_SPEED', '30')) # Average speed in km/h
                }
            BASE_FARE = create_trip._config_cache['BASE_FARE']
            RATE_PER_KM = create_trip._config_cache['RATE_PER_KM']
            AVERAGE_SPEED = create_trip._config_cache['AVERAGE_SPEED']
        except:
            # Fallback values if config is unavailable
            BASE_FARE = 200      # KES base fare
            RATE_PER_KM = 50     # KES per kilometer
            AVERAGE_SPEED = 30   # km/h average city speed
        
        # Calculate total fare: base fare + distance-based pricing
        fare = BASE_FARE + (distance * RATE_PER_KM)
        
        # Estimate trip duration based on distance and average speed
        duration = int((distance / AVERAGE_SPEED) * 60)  # Convert hours to minutes
        
        # Create new trip record with all calculated values
        trip = Trip(
            passenger_id=user_id,                    # Link to requesting passenger
            pickup_lat=pickup['lat'],                # Pickup coordinates
            pickup_lng=pickup['lng'],
            pickup_address=pickup['address'],        # Human-readable pickup address
            dropoff_lat=dropoff['lat'],              # Destination coordinates
            dropoff_lng=dropoff['lng'],
            dropoff_address=dropoff['address'],      # Human-readable destination
            fare=round(fare, 2),                     # Calculated fare in KES
            distance=round(distance, 2),             # Distance in kilometers
            duration=duration,                       # Estimated duration in minutes
            status='requested'                       # Initial trip status
        )
        
        # Save trip to database
        db.session.add(trip)
        db.session.commit()
        
        # Optional: Notify nearby drivers if requested
        # This could be extended to send push notifications or SMS
        if data.get('notifyDrivers'):
            # Find available drivers (online and approved)
            online_drivers = Driver.query.filter_by(is_online=True, status='approved').all()
            # TODO: Implement driver notification system (push notifications, SMS, etc.)
        
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
    finally:
        try:
            db.session.close()
        except:
            pass

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
        
        # Build query based on user role for data access control
        if user.role == 'passenger':
            # Passengers can only see their own trips
            query = Trip.query.filter_by(passenger_id=user_id)
        elif user.role == 'driver':
            # Drivers can only see trips they're assigned to
            query = Trip.query.filter_by(driver_id=user_id)
        else:  # admin role
            # Admins can see all trips in the system
            query = Trip.query
        
        # Apply status filter if provided
        if status:
            query = query.filter_by(status=status)
        
        # Optimize query with eager loading to prevent N+1 queries
        # Load passenger and driver data in single query
        trips = query.options(
            db.joinedload(Trip.passenger),  # Load passenger info
            db.joinedload(Trip.driver)      # Load driver info
        ).order_by(Trip.created_at.desc()).limit(limit).offset((page-1)*limit).all()
        
        # Get total count for pagination metadata
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
    finally:
        try:
            db.session.close()
        except:
            pass

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
        
        # Verify user is a driver - only drivers can accept trips
        if user.role != 'driver':
            return jsonify({
                'success': False,
                'error': {
                    'code': 'UNAUTHORIZED',
                    'message': 'Only drivers can accept trips'
                }
            }), 403
        
        # Find the requested trip
        trip = Trip.query.get(trip_id)
        
        # Validate trip exists
        if not trip:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'TRIP_NOT_FOUND',
                    'message': 'Trip not found'
                }
            }), 404
        
        # Ensure trip is still available for acceptance
        if trip.status != 'requested':
            return jsonify({
                'success': False,
                'error': {
                    'code': 'INVALID_STATUS',
                    'message': 'Trip is not available'
                }
            }), 400
        
        # Accept the trip - assign driver and update status
        trip.driver_id = user_id                    # Assign current driver
        trip.status = 'accepted'                    # Change status to accepted
        trip.accepted_at = datetime.utcnow()        # Record acceptance timestamp
        
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
    finally:
        try:
            db.session.close()
        except:
            pass

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
        
        # Verify trip exists and user is the assigned driver
        if not trip or trip.driver_id != user_id:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'UNAUTHORIZED',
                    'message': 'Unauthorized'
                }
            }), 403
        
        # Mark trip as completed
        trip.status = 'completed'
        trip.completed_at = datetime.utcnow()
        
        # Handle payment status based on system configuration
        try:
            from models import Config
            # Check if auto-payment completion is enabled
            auto_payment = Config.get_value('AUTO_COMPLETE_PAYMENT', 'true').lower() == 'true'
            trip.payment_status = 'paid' if auto_payment else 'pending'
        except:
            # Default to paid status if config unavailable
            trip.payment_status = 'paid'
        
        # Update driver performance statistics using relationship
        if trip.driver and hasattr(trip.driver, 'driver_profile'):
            driver = trip.driver.driver_profile
            if driver:
                driver.total_trips += 1              # Increment completed trips count
                driver.total_earnings += trip.fare   # Add trip fare to total earnings
        else:
            # Fallback to query if relationship not available
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
    finally:
        try:
            db.session.close()
        except:
            pass

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
        # Find trip with eager loading for efficient data access
        trip = Trip.query.options(
            db.joinedload(Trip.passenger),
            db.joinedload(Trip.driver)
        ).get(trip_id)
        
        # Verify trip exists and user is the passenger who took the trip
        if not trip or trip.passenger_id != user_id:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'UNAUTHORIZED',
                    'message': 'Unauthorized - Only trip passengers can rate' }
            }), 403
        
        # Extract rating data from request
        data = request.json
        rating = data.get('rating')
        feedback = data.get('feedback', '')  # Optional feedback text
        
        # Validate rating is within acceptable range (1-5 stars)
        if not rating or rating < 1 or rating > 5:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'INVALID_RATING',
                    'message': 'Rating must be between 1 and 5'
                }
            }), 400
        
        # Save rating and feedback to trip record
        trip.rating = rating
        trip.feedback = feedback
        
        # Update driver's overall rating based on all their trips
        if trip.driver_id:
            driver = Driver.query.filter_by(user_id=trip.driver_id).first()
            if driver:
                # Calculate new average rating efficiently using SQL aggregate function
                avg_rating = db.session.query(db.func.avg(Trip.rating)).filter(
                    Trip.driver_id == trip.driver_id,    # Only this driver's trips
                    Trip.rating.isnot(None)              # Only rated trips
                ).scalar()
                
                # Update driver's rating (rounded to 2 decimal places)
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
    finally:
        try:
            db.session.close()
        except:
            pass

@trips_bp.route('/available', methods=['GET'])
@jwt_required()
def get_available_trips():
    """
    Get available trips for drivers to accept
    
    This endpoint shows all unassigned trip requests that drivers can accept.
    Only drivers can access this endpoint for security.
    
    Returns:
        JSON: List of available trips with passenger information
    """
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        # Security check: Only drivers can view available trips
        if user.role != 'driver':
            return jsonify({
                'success': False,
                'error': {
                    'code': 'UNAUTHORIZED',
                    'message': 'Only drivers can view available trips'
                }
            }), 403
        
        # Query for unassigned trips with passenger info preloaded
        # Filters: status='requested' (new requests) AND driver_id=None (unassigned)
        trips = Trip.query.options(
            db.joinedload(Trip.passenger)  # Preload passenger data to avoid N+1 queries
        ).filter_by(
            status='requested',    # Only new trip requests
            driver_id=None        # Only unassigned trips
        ).order_by(
            Trip.created_at.desc()  # Show newest requests first
        ).limit(20).all()           # Limit to 20 for performance
        
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
    finally:
        try:
            db.session.close()
        except:
            pass

@trips_bp.route('/<trip_id>', methods=['GET'])
@jwt_required()
def get_trip(trip_id):
    """
    Get detailed information for a specific trip
    
    Allows users to view trip details with proper authorization:
    - Passengers can view their own trips
    - Drivers can view trips they're assigned to
    - Admins can view any trip
    
    Args:
        trip_id (str): Unique identifier for the trip
    
    Returns:
        JSON: Complete trip information including passenger/driver details
    """
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        # Find the requested trip with eager loading to prevent N+1 queries
        trip = Trip.query.options(
            db.joinedload(Trip.passenger),
            db.joinedload(Trip.driver)
        ).get(trip_id)
        if not trip:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'NOT_FOUND',
                    'message': 'Trip not found'
                }
            }), 404
        
        # Authorization check: Only allow access to relevant users
        # Admin: can view any trip
        # Passenger: can only view their own trips
        # Driver: can only view trips they're assigned to
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
    finally:
        try:
            db.session.close()
        except:
            pass

@trips_bp.route('/<trip_id>', methods=['PUT'])
@jwt_required()
def update_trip(trip_id):
    """
    Update trip status and details
    
    Allows drivers to update trip status during the ride lifecycle.
    Common status updates:
    - 'driving': Driver has started the trip
    - 'completed': Trip has been finished
    
    Args:
        trip_id (str): Unique identifier for the trip
    
    Returns:
        JSON: Updated trip information
    """
    try:
        user_id = get_jwt_identity()
        # Load trip with relationships to prevent additional queries
        trip = Trip.query.options(
            db.joinedload(Trip.passenger),
            db.joinedload(Trip.driver)
        ).get(trip_id)
        
        # Validate trip exists
        if not trip:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'NOT_FOUND',
                    'message': 'Trip not found'
                }
            }), 404
        
        # Security check: Only the assigned driver can update trip status
        if trip.driver_id != user_id:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'UNAUTHORIZED',
                    'message': 'Only assigned driver can update trip'
                }
            }), 403
        
        # Process status update
        data = request.json
        if 'status' in data:
            trip.status = data['status']
            
            # Special handling for 'driving' status - record trip start time
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
    finally:
        try:
            db.session.close()
        except:
            pass

@trips_bp.route('/<trip_id>', methods=['DELETE'])
@jwt_required()
def delete_trip(trip_id):
    """
    Cancel a trip (soft delete by changing status)
    
    Allows authorized users to cancel trips that haven't been completed.
    Authorization rules:
    - Passengers can cancel their own trips
    - Drivers can cancel trips they're assigned to
    - Admins can cancel any trip
    
    Args:
        trip_id (str): Unique identifier for the trip to cancel
    
    Returns:
        JSON: Confirmation of trip cancellation
    
    Note:
        This is a soft delete - the trip record remains but status changes to 'cancelled'
    """
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        # Load trip with relationships for efficient access
        trip = Trip.query.options(
            db.joinedload(Trip.passenger),
            db.joinedload(Trip.driver)
        ).get(trip_id)
        
        # Validate trip exists
        if not trip:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'NOT_FOUND',
                    'message': 'Trip not found'
                }
            }), 404
        
        # Authorization check: Only relevant parties can cancel
        # Admin: can cancel any trip
        # Passenger: can cancel their own trip
        # Driver: can cancel trips they're assigned to
        if user.role != 'admin' and trip.passenger_id != user_id and trip.driver_id != user_id:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'UNAUTHORIZED',
                    'message': 'Unauthorized to cancel this trip'
                }
            }), 403
        
        # Business rule: Cannot cancel completed trips
        if trip.status == 'completed':
            return jsonify({
                'success': False,
                'error': {
                    'code': 'INVALID_STATUS',
                    'message': 'Cannot cancel completed trip'
                }
            }), 400
        
        # Perform soft delete by changing status to cancelled
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
    finally:
        try:
            db.session.close()
        except:
            pass