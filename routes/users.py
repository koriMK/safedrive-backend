from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import User, db

users_bp = Blueprint('users', __name__)

@users_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_user_profile():
    """
    Get user profile
    ---
    tags:
      - Users
    security:
      - Bearer: []
    responses:
      200:
        description: User profile retrieved successfully
      404:
        description: User not found
    """
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'USER_NOT_FOUND',
                    'message': 'User not found'
                }
            }), 404
        
        return jsonify({
            'success': True,
            'data': user.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'FETCH_FAILED',
                'message': str(e)
            }
        }), 500

@users_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_user_profile():
    """
    Update user profile
    ---
    tags:
      - Users
    security:
      - Bearer: []
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            name:
              type: string
              example: "John Doe"
            phone:
              type: string
              example: "+254712345678"
    responses:
      200:
        description: Profile updated successfully
      404:
        description: User not found
      409:
        description: Phone number already in use
    """
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'USER_NOT_FOUND',
                    'message': 'User not found'
                }
            }), 404
        
        data = request.json
        
        # Update allowed fields
        if 'name' in data:
            user.name = data['name']
        if 'phone' in data:
            # Check if phone is already taken by another user
            existing_user = User.query.filter(
                User.phone == data['phone'],
                User.id != user_id
            ).first()
            if existing_user:
                return jsonify({
                    'success': False,
                    'error': {
                        'code': 'PHONE_EXISTS',
                        'message': 'Phone number already in use'
                    }
                }), 409
            user.phone = data['phone']
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Profile updated successfully',
            'data': user.to_dict()
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

@users_bp.route('', methods=['GET'])
@jwt_required()
def get_users():
    """
    Get all users (admin only)
    ---
    tags:
      - Users
    security:
      - Bearer: []
    responses:
      200:
        description: Users retrieved successfully
      403:
        description: Admin access required
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
        
        users = User.query.all()
        
        return jsonify({
            'success': True,
            'data': [user.to_dict() for user in users]
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'FETCH_FAILED',
                'message': str(e)
            }
        }), 500

@users_bp.route('/<user_id>', methods=['GET'])
@jwt_required()
def get_user(user_id):
    """
    Get specific user (admin only)
    ---
    tags:
      - Users
    security:
      - Bearer: []
    parameters:
      - name: user_id
        in: path
        type: string
        required: true
        description: User ID
    responses:
      200:
        description: User retrieved successfully
      403:
        description: Admin access required
      404:
        description: User not found
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
        
        user = User.query.get(user_id)
        if not user:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'NOT_FOUND',
                    'message': 'User not found'
                }
            }), 404
        
        return jsonify({
            'success': True,
            'data': user.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'FETCH_FAILED',
                'message': str(e)
            }
        }), 500

@users_bp.route('/<user_id>', methods=['DELETE'])
@jwt_required()
def delete_user(user_id):
    """
    Delete user (admin only)
    ---
    tags:
      - Users
    security:
      - Bearer: []
    parameters:
      - name: user_id
        in: path
        type: string
        required: true
        description: User ID
    responses:
      200:
        description: User deleted successfully
      403:
        description: Admin access required
      404:
        description: User not found
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
        
        user = User.query.get(user_id)
        if not user:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'NOT_FOUND',
                    'message': 'User not found'
                }
            }), 404
        
        db.session.delete(user)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'User deleted'
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