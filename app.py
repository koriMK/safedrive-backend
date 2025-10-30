from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
# from flasgger import Swagger
import os

# Initialize extensions
jwt = JWTManager()

def create_app():
    """Application factory"""
    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', f'sqlite:///{os.path.join(os.path.dirname(os.path.abspath(__file__)), "safedrive.db")}')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
        'connect_args': {'check_same_thread': False} if 'sqlite' in os.environ.get('DATABASE_URL', '') else {}
    }
    app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'jwt-secret-key-change-in-production')
    
    # Initialize extensions
    from models import db
    db.init_app(app)
    jwt.init_app(app)
    CORS(app, 
         resources={r"/api/*": {"origins": "*"}},
         allow_headers=["Content-Type", "Authorization"],
         methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])
    
    # Swagger disabled for faster deployment
    # Will re-enable after successful deployment
    
    # Database setup
    with app.app_context():
        try:
            db.create_all()
        except Exception:
            pass
    
    # Register blueprints
    from routes.auth import auth_bp
    from routes.users import users_bp
    from routes.trips import trips_bp
    from routes.drivers import drivers_bp
    from routes.payments import payments_bp
    from routes.admin import admin_bp
    from routes.notifications import notifications_bp
    from routes.ratings import ratings_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/v1/auth')
    app.register_blueprint(users_bp, url_prefix='/api/v1/users')
    app.register_blueprint(trips_bp, url_prefix='/api/v1/trips')
    app.register_blueprint(drivers_bp, url_prefix='/api/v1/drivers')
    app.register_blueprint(payments_bp, url_prefix='/api/v1/payments')
    app.register_blueprint(admin_bp, url_prefix='/api/v1/admin')
    app.register_blueprint(notifications_bp, url_prefix='/api/v1/notifications')
    app.register_blueprint(ratings_bp, url_prefix='/api/v1/ratings')
    
    # Migration endpoint
    from routes.migrate import migrate_bp
    app.register_blueprint(migrate_bp, url_prefix='/api/v1/migrate')
    
    # Health check endpoint
    @app.route('/api/v1/health')
    def health_check():
        """
        Health check endpoint
        ---
        tags:
          - System
        responses:
          200:
            description: Service is healthy
        """
        return jsonify({
            'status': 'healthy',
            'version': '1.0.0'
        }), 200
    
    # API documentation endpoint
    @app.route('/')
    def api_docs():
        """
        API documentation and endpoints overview
        ---
        tags:
          - System
        responses:
          200:
            description: API information and available endpoints
        """
        return jsonify({
            'message': 'SafeDrive API v1.0',
            'documentation': 'https://github.com/koriMK/safedrive-backend/blob/main/API_DOCUMENTATION.md',
            'swagger_ui': '/docs/',
            'base_url': '/api/v1',
            'endpoints': {
                'auth': {
                    'login': 'POST /api/v1/auth/login',
                    'register': 'POST /api/v1/auth/register',
                    'profile': 'GET /api/v1/auth/me'
                },
                'trips': {
                    'create': 'POST /api/v1/trips',
                    'list': 'GET /api/v1/trips',
                    'available': 'GET /api/v1/trips/available',
                    'accept': 'PUT /api/v1/trips/{id}/accept',
                    'complete': 'PUT /api/v1/trips/{id}/complete'
                },
                'payments': {
                    'initiate': 'POST /api/v1/payments/initiate',
                    'status': 'GET /api/v1/payments/status/{id}'
                },
                'drivers': {
                    'profile': 'GET /api/v1/drivers/profile',
                    'upload': 'POST /api/v1/drivers/upload-document',
                    'earnings': 'GET /api/v1/drivers/earnings'
                },
                'admin': {
                    'stats': 'GET /api/v1/admin/stats'
                }
            },
            'authentication': 'Bearer JWT token required for protected endpoints'
        }), 200
    
    # Global error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'success': False,
            'error': {
                'code': 'NOT_FOUND',
                'message': 'Resource not found'
            }
        }), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        try:
            db.session.rollback()
        except:
            pass
        return jsonify({
            'success': False,
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': 'Internal server error'
            }
        }), 500
    
    return app

# Create app instance for Gunicorn
app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5002))
    app.run(debug=False, host='0.0.0.0', port=port)