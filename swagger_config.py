from flask_restx import Api, Resource, fields
from flask import Blueprint

# Create Swagger API blueprint
swagger_bp = Blueprint('swagger', __name__)

# Initialize API with Swagger UI
api = Api(
    swagger_bp,
    version='1.0',
    title='SafeDrive API',
    description='Complete REST API for SafeDrive ride-sharing platform',
    doc='/docs/',
    authorizations={
        'Bearer': {
            'type': 'apiKey',
            'in': 'header',
            'name': 'Authorization',
            'description': 'JWT Authorization header using the Bearer scheme. Example: "Authorization: Bearer {token}"'
        }
    },
    security='Bearer'
)

# Define common models
location_model = api.model('Location', {
    'lat': fields.Float(required=True, description='Latitude'),
    'lng': fields.Float(required=True, description='Longitude'),
    'address': fields.String(required=True, description='Address')
})

trip_request_model = api.model('TripRequest', {
    'pickup': fields.Nested(location_model, required=True),
    'dropoff': fields.Nested(location_model, required=True),
    'notifyDrivers': fields.Boolean(default=True)
})

user_model = api.model('User', {
    'id': fields.String(description='User ID'),
    'email': fields.String(description='Email'),
    'name': fields.String(description='Full name'),
    'phone': fields.String(description='Phone number'),
    'role': fields.String(description='User role'),
    'createdAt': fields.String(description='Creation timestamp')
})

trip_model = api.model('Trip', {
    'id': fields.String(description='Trip ID'),
    'passengerId': fields.String(description='Passenger ID'),
    'driverId': fields.String(description='Driver ID'),
    'pickup': fields.Nested(location_model),
    'dropoff': fields.Nested(location_model),
    'status': fields.String(description='Trip status'),
    'fare': fields.Float(description='Trip fare'),
    'distance': fields.Float(description='Distance in km'),
    'duration': fields.Integer(description='Duration in minutes'),
    'paymentStatus': fields.String(description='Payment status'),
    'createdAt': fields.String(description='Creation timestamp')
})

payment_request_model = api.model('PaymentRequest', {
    'tripId': fields.String(required=True, description='Trip ID'),
    'phone': fields.String(required=True, description='Phone number (+254XXXXXXXXX)'),
    'amount': fields.Float(required=True, description='Payment amount')
})

login_model = api.model('Login', {
    'email': fields.String(required=True, description='User email'),
    'password': fields.String(required=True, description='User password')
})

register_model = api.model('Register', {
    'name': fields.String(required=True, description='Full name'),
    'email': fields.String(required=True, description='Email address'),
    'password': fields.String(required=True, description='Password'),
    'phone': fields.String(description='Phone number'),
    'role': fields.String(required=True, description='User role (passenger/driver)')
})

error_model = api.model('Error', {
    'success': fields.Boolean(default=False),
    'error': fields.Raw(description='Error details')
})

success_model = api.model('Success', {
    'success': fields.Boolean(default=True),
    'message': fields.String(description='Success message'),
    'data': fields.Raw(description='Response data')
})