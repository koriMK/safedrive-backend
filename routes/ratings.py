from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import Rating, Trip, User, Driver, db

ratings_bp = Blueprint('ratings', __name__)

@ratings_bp.route('', methods=['POST'])
@jwt_required()
def create_rating():
    """
    Create trip rating
    ---
    tags:
      - Ratings
    security:
      - Bearer: []
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - tripId
          properties:
            tripId:
              type: string
              example: "t_123456789abc"
            passengerRating:
              type: integer
              minimum: 1
              maximum: 5
              example: 5
            driverRating:
              type: integer
              minimum: 1
              maximum: 5
              example: 4
            passengerFeedback:
              type: string
              example: "Great passenger!"
            driverFeedback:
              type: string
              example: "Excellent driver, very professional"
            cleanlinessRating:
              type: integer
              minimum: 1
              maximum: 5
              example: 5
            punctualityRating:
              type: integer
              minimum: 1
              maximum: 5
              example: 4
            communicationRating:
              type: integer
              minimum: 1
              maximum: 5
              example: 5
            safetyRating:
              type: integer
              minimum: 1
              maximum: 5
              example: 5
    responses:
      201:
        description: Rating created successfully
      400:
        description: Validation error
      404:
        description: Trip not found
    """
    try:
        user_id = get_jwt_identity()
        data = request.json
        trip_id = data.get('tripId')
        
        # Verify trip exists and user is involved
        trip = Trip.query.get(trip_id)
        if not trip or (trip.passenger_id != user_id and trip.driver_id != user_id):
            return jsonify({
                'success': False,
                'error': {
                    'code': 'TRIP_NOT_FOUND',
                    'message': 'Trip not found or unauthorized'
                }
            }), 404
        
        # Check if rating already exists
        existing_rating = Rating.query.filter_by(trip_id=trip_id).first()
        if existing_rating:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'RATING_EXISTS',
                    'message': 'Rating already exists for this trip'
                }
            }), 400
        
        rating = Rating(
            trip_id=trip_id,
            passenger_rating=data.get('passengerRating'),
            driver_rating=data.get('driverRating'),
            passenger_feedback=data.get('passengerFeedback'),
            driver_feedback=data.get('driverFeedback'),
            cleanliness_rating=data.get('cleanlinessRating'),
            punctuality_rating=data.get('punctualityRating'),
            communication_rating=data.get('communicationRating'),
            safety_rating=data.get('safetyRating')
        )
        
        db.session.add(rating)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Rating created',
            'data': rating.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': {
                'code': 'CREATE_FAILED',
                'message': str(e)
            }
        }), 500

@ratings_bp.route('', methods=['GET'])
@jwt_required()
def get_ratings():
    """
    Get user's ratings
    ---
    tags:
      - Ratings
    security:
      - Bearer: []
    responses:
      200:
        description: Ratings retrieved successfully
    """
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        # Get ratings based on user role
        if user.role == 'passenger':
            # Get ratings for trips where user was passenger
            ratings = db.session.query(Rating).join(Trip).filter(Trip.passenger_id == user_id).all()
        elif user.role == 'driver':
            # Get ratings for trips where user was driver
            ratings = db.session.query(Rating).join(Trip).filter(Trip.driver_id == user_id).all()
        else:
            # Admin can see all ratings
            ratings = Rating.query.all()
        
        return jsonify({
            'success': True,
            'data': [rating.to_dict() for rating in ratings]
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'FETCH_FAILED',
                'message': str(e)
            }
        }), 500

@ratings_bp.route('/<rating_id>', methods=['GET'])
@jwt_required()
def get_rating(rating_id):
    """
    Get specific rating
    ---
    tags:
      - Ratings
    security:
      - Bearer: []
    parameters:
      - name: rating_id
        in: path
        type: string
        required: true
        description: Rating ID
    responses:
      200:
        description: Rating retrieved successfully
      404:
        description: Rating not found
    """
    try:
        rating = Rating.query.get(rating_id)
        
        if not rating:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'NOT_FOUND',
                    'message': 'Rating not found'
                }
            }), 404
        
        return jsonify({
            'success': True,
            'data': rating.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'FETCH_FAILED',
                'message': str(e)
            }
        }), 500

@ratings_bp.route('/<rating_id>', methods=['PUT'])
@jwt_required()
def update_rating(rating_id):
    """
    Update rating
    ---
    tags:
      - Ratings
    security:
      - Bearer: []
    parameters:
      - name: rating_id
        in: path
        type: string
        required: true
        description: Rating ID
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            passengerRating:
              type: integer
              minimum: 1
              maximum: 5
            driverRating:
              type: integer
              minimum: 1
              maximum: 5
            passengerFeedback:
              type: string
            driverFeedback:
              type: string
            cleanlinessRating:
              type: integer
              minimum: 1
              maximum: 5
            punctualityRating:
              type: integer
              minimum: 1
              maximum: 5
            communicationRating:
              type: integer
              minimum: 1
              maximum: 5
            safetyRating:
              type: integer
              minimum: 1
              maximum: 5
    responses:
      200:
        description: Rating updated successfully
      404:
        description: Rating not found
    """
    try:
        user_id = get_jwt_identity()
        rating = Rating.query.get(rating_id)
        
        if not rating:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'NOT_FOUND',
                    'message': 'Rating not found'
                }
            }), 404
        
        # Verify user is involved in the trip
        trip = Trip.query.get(rating.trip_id)
        if not trip or (trip.passenger_id != user_id and trip.driver_id != user_id):
            return jsonify({
                'success': False,
                'error': {
                    'code': 'UNAUTHORIZED',
                    'message': 'Unauthorized to update this rating'
                }
            }), 403
        
        data = request.json
        
        # Update fields if provided
        if 'passengerRating' in data:
            rating.passenger_rating = data['passengerRating']
        if 'driverRating' in data:
            rating.driver_rating = data['driverRating']
        if 'passengerFeedback' in data:
            rating.passenger_feedback = data['passengerFeedback']
        if 'driverFeedback' in data:
            rating.driver_feedback = data['driverFeedback']
        if 'cleanlinessRating' in data:
            rating.cleanliness_rating = data['cleanlinessRating']
        if 'punctualityRating' in data:
            rating.punctuality_rating = data['punctualityRating']
        if 'communicationRating' in data:
            rating.communication_rating = data['communicationRating']
        if 'safetyRating' in data:
            rating.safety_rating = data['safetyRating']
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Rating updated',
            'data': rating.to_dict()
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

@ratings_bp.route('/<rating_id>', methods=['DELETE'])
@jwt_required()
def delete_rating(rating_id):
    """
    Delete rating
    ---
    tags:
      - Ratings
    security:
      - Bearer: []
    parameters:
      - name: rating_id
        in: path
        type: string
        required: true
        description: Rating ID
    responses:
      200:
        description: Rating deleted successfully
      404:
        description: Rating not found
    """
    try:
        user_id = get_jwt_identity()
        rating = Rating.query.get(rating_id)
        
        if not rating:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'NOT_FOUND',
                    'message': 'Rating not found'
                }
            }), 404
        
        # Verify user is involved in the trip or is admin
        trip = Trip.query.get(rating.trip_id)
        user = User.query.get(user_id)
        if not trip or (trip.passenger_id != user_id and trip.driver_id != user_id and user.role != 'admin'):
            return jsonify({
                'success': False,
                'error': {
                    'code': 'UNAUTHORIZED',
                    'message': 'Unauthorized to delete this rating'
                }
            }), 403
        
        db.session.delete(rating)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Rating deleted'
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