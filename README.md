# SafeDrive Backend

Flask-based REST API backend for the SafeDrive ride-sharing application.

## Features

- **RESTful API**: Complete CRUD operations for all entities
- **JWT Authentication**: Secure token-based authentication
- **Role-based Access**: Passenger, Driver, and Admin roles
- **M-Pesa Integration**: Real Daraja API integration for payments
- **File Upload**: Driver document management system
- **Database ORM**: SQLAlchemy with SQLite/PostgreSQL support

## Technology Stack

- **Flask** - Python web framework
- **SQLAlchemy** - Database ORM
- **Flask-JWT-Extended** - JWT authentication
- **Flask-CORS** - Cross-origin resource sharing
- **Requests** - HTTP client for M-Pesa API
- **SQLite** - Development database
- **Werkzeug** - Password hashing and file uploads

## Getting Started

### Prerequisites

- Python 3.8+
- pip (Python package manager)

### Installation

1. Clone the repository:
```bash
git clone git@github.com:koriMK/safedrive-backend.git
cd safedrive-backend
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Initialize database:
```bash
python app.py
```

5. The server will start on [http://localhost:5002](http://localhost:5002)

## Project Structure

```
├── app.py                 # Flask application factory
├── models.py              # Database models
├── routes/                # API route handlers
│   ├── auth.py           # Authentication endpoints
│   ├── users.py          # User management
│   ├── drivers.py        # Driver operations
│   ├── trips.py          # Trip management
│   ├── payments.py       # Payment processing
│   └── admin.py          # Admin operations
├── services/             # Business logic services
│   └── mpesa.py          # M-Pesa integration
├── uploads/              # File storage directory
└── requirements.txt      # Python dependencies
```

## API Endpoints

### Authentication
- `POST /api/v1/auth/register` - User registration
- `POST /api/v1/auth/login` - User login
- `GET /api/v1/auth/me` - Get current user

### Trip Management
- `POST /api/v1/trips` - Create trip request
- `GET /api/v1/trips` - Get user trips
- `GET /api/v1/trips/available` - Get available trips (drivers)
- `PUT /api/v1/trips/{id}/accept` - Accept trip
- `PUT /api/v1/trips/{id}/complete` - Complete trip

### Payment Processing
- `POST /api/v1/payments/initiate` - Initiate M-Pesa payment
- `GET /api/v1/payments/status/{id}` - Check payment status
- `POST /api/v1/payments/callback` - M-Pesa callback handler

### Driver Operations
- `GET /api/v1/drivers/profile` - Get driver profile
- `PUT /api/v1/drivers/profile` - Update driver profile
- `POST /api/v1/drivers/upload-document` - Upload KYC documents
- `PUT /api/v1/drivers/status` - Update online status

### Admin Operations
- `GET /api/v1/admin/stats` - System statistics
- `GET /api/v1/admin/drivers` - Driver management
- `PUT /api/v1/admin/drivers/{id}/approve` - Approve driver
- `PUT /api/v1/admin/drivers/{id}/reject` - Reject driver

## Database Schema

### Users Table
- Multi-role support (passenger, driver, admin)
- JWT authentication with password hashing
- Phone number optional for admin users

### Drivers Table
- Vehicle information storage
- Document verification status
- Performance metrics (rating, trips, earnings)

### Trips Table
- Geographic coordinates for pickup/dropoff
- Fare calculation and storage
- Status tracking throughout trip lifecycle

### Payments Table
- M-Pesa transaction tracking
- STK Push integration
- Payment status management

## M-Pesa Integration

### Daraja API Configuration
```python
# Sandbox credentials (replace with production for live)
CONSUMER_KEY = "UnDvUCktXcQDyRScx0uAnJlA7rboMWhSnAxvhSOYQiX8QU0t"
CONSUMER_SECRET = "eP7nwvhM3OwL0nVhRlOCsGnRawPi32BkENmT33NygDpdYdq5sy1WyAshdCnidCkb"
BUSINESS_SHORTCODE = "174379"
```

### STK Push Flow
1. Generate OAuth access token
2. Create STK Push request
3. Customer receives payment prompt
4. Query payment status
5. Handle callback confirmation

## Environment Variables

Create a `.env` file:

```env
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-key
DATABASE_URL=sqlite:///safedrive.db
UPLOAD_FOLDER=uploads
MPESA_CONSUMER_KEY=your-mpesa-consumer-key
MPESA_CONSUMER_SECRET=your-mpesa-consumer-secret
```

## Testing

### Manual Testing
```bash
# Test user registration
curl -X POST http://localhost:5002/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"name":"Test User","email":"test@example.com","password":"password123","role":"passenger"}'

# Test login
curl -X POST http://localhost:5002/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}'
```

### Database Verification
```bash
python check_database.py
```

## Deployment

### Production Setup

1. **Environment Configuration**:
```bash
export FLASK_ENV=production
export SECRET_KEY=your-production-secret-key
```

2. **Database Migration**:
```bash
# For PostgreSQL in production
pip install psycopg2
export DATABASE_URL=postgresql://user:password@localhost/safedrive
```

3. **WSGI Server**:
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5002 app:app
```

### Docker Deployment
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5002
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5002", "app:app"]
```

## Security Considerations

- **JWT Tokens**: Secure token generation and validation
- **Password Hashing**: Werkzeug secure password hashing
- **Input Validation**: Comprehensive request validation
- **CORS Configuration**: Proper cross-origin setup
- **File Upload Security**: Secure file handling and validation

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For support and questions, please open an issue on GitHub.