from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import Notification, db
from datetime import datetime

notifications_bp = Blueprint('notifications', __name__)

@notifications_bp.route('', methods=['POST'])
@jwt_required()
def create_notification():
    """
    Create notification
    ---
    tags:
      - Notifications
    security:
      - Bearer: []
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - title
            - message
            - type
          properties:
            title:
              type: string
              example: "Trip Request"
            message:
              type: string
              example: "You have a new trip request"
            type:
              type: string
              enum: ["trip_request", "payment", "system", "driver_approved"]
              example: "trip_request"
            tripId:
              type: string
              example: "t_123456789abc"
            paymentId:
              type: string
              example: "pay_123456789abc"
    responses:
      201:
        description: Notification created successfully
      400:
        description: Validation error
    """
    try:
        user_id = get_jwt_identity()
        data = request.json
        
        notification = Notification(
            user_id=user_id,
            title=data['title'],
            message=data['message'],
            type=data['type'],
            trip_id=data.get('tripId'),
            payment_id=data.get('paymentId')
        )
        
        db.session.add(notification)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Notification created',
            'data': notification.to_dict()
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

@notifications_bp.route('', methods=['GET'])
@jwt_required()
def get_notifications():
    """
    Get user notifications
    ---
    tags:
      - Notifications
    security:
      - Bearer: []
    parameters:
      - name: unread_only
        in: query
        type: boolean
        default: false
        description: Get only unread notifications
    responses:
      200:
        description: Notifications retrieved successfully
    """
    try:
        user_id = get_jwt_identity()
        unread_only = request.args.get('unread_only', 'false').lower() == 'true'
        
        query = Notification.query.filter_by(user_id=user_id)
        if unread_only:
            query = query.filter_by(is_read=False)
        
        notifications = query.order_by(Notification.created_at.desc()).all()
        
        return jsonify({
            'success': True,
            'data': [notification.to_dict() for notification in notifications]
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'FETCH_FAILED',
                'message': str(e)
            }
        }), 500

@notifications_bp.route('/<notification_id>', methods=['PUT'])
@jwt_required()
def update_notification(notification_id):
    """
    Update notification (mark as read)
    ---
    tags:
      - Notifications
    security:
      - Bearer: []
    parameters:
      - name: notification_id
        in: path
        type: string
        required: true
        description: Notification ID
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            isRead:
              type: boolean
              example: true
    responses:
      200:
        description: Notification updated successfully
      404:
        description: Notification not found
    """
    try:
        user_id = get_jwt_identity()
        notification = Notification.query.filter_by(id=notification_id, user_id=user_id).first()
        
        if not notification:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'NOT_FOUND',
                    'message': 'Notification not found'
                }
            }), 404
        
        data = request.json
        if 'isRead' in data:
            notification.is_read = data['isRead']
            if data['isRead']:
                notification.read_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Notification updated',
            'data': notification.to_dict()
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

@notifications_bp.route('/<notification_id>', methods=['DELETE'])
@jwt_required()
def delete_notification(notification_id):
    """
    Delete notification
    ---
    tags:
      - Notifications
    security:
      - Bearer: []
    parameters:
      - name: notification_id
        in: path
        type: string
        required: true
        description: Notification ID
    responses:
      200:
        description: Notification deleted successfully
      404:
        description: Notification not found
    """
    try:
        user_id = get_jwt_identity()
        notification = Notification.query.filter_by(id=notification_id, user_id=user_id).first()
        
        if not notification:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'NOT_FOUND',
                    'message': 'Notification not found'
                }
            }), 404
        
        db.session.delete(notification)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Notification deleted'
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