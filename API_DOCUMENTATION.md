# SafeDrive API Documentation

## Base URL
```
https://safedrive-backend-d579.onrender.com/api/v1
```

## Interactive Documentation
**Swagger UI**: https://safedrive-backend-d579.onrender.com/api/v1/docs/

## Authentication
All protected endpoints require JWT Bearer token:
```
Authorization: Bearer <your_jwt_token>
```

---

## 🔐 Authentication Endpoints

### POST /auth/register
Register a new user account.

**Request Body:**
```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "password": "password123",
  "phone": "+254712345678",
  "role": "passenger"
}
```

**Response (201):**
```json
{
  "success": true,
  "message": "User registered successfully",
  "data": {
    "user": {
      "id": "u_abc123",
      "email": "john@example.com",
      "name": "John Doe",
      "role": "passenger"
    },
    "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
  }
}
```

### POST /auth/login
Authenticate user and get JWT token.

**Request Body:**
```json
{
  "email": "john@example.com",
  "password": "password123"
}
```

**Response (200):**
```json
{
  "success": true,
  "message": "Login successful",
  "data": {
    "user": {
      "id": "u_abc123",
      "email": "john@example.com",
      "name": "John Doe",
      "role": "passenger"
    },
    "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
  }
}
```

### GET /auth/me
Get current authenticated user profile.

**Headers:** `Authorization: Bearer <token>`

**Response (200):**
```json
{
  "success": true,
  "data": {
    "id": "u_abc123",
    "email": "john@example.com",
    "name": "John Doe",
    "phone": "+254712345678",
    "role": "passenger",
    "createdAt": "2024-01-15T10:30:00Z"
  }
}
```

---

## 🚗 Trip Management Endpoints

### POST /trips
Create a new trip request (Passengers only).

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "pickup": {
    "lat": -1.2921,
    "lng": 36.8219,
    "address": "Nairobi CBD, Kenya"
  },
  "dropoff": {
    "lat": -1.3032,
    "lng": 36.8856,
    "address": "Westlands, Nairobi"
  },
  "notifyDrivers": true
}
```

**Response (201):**
```json
{
  "success": true,
  "message": "Trip requested successfully",
  "data": {
    "id": "t_xyz789",
    "passengerId": "u_abc123",
    "pickup": {
      "lat": -1.2921,
      "lng": 36.8219,
      "address": "Nairobi CBD, Kenya"
    },
    "dropoff": {
      "lat": -1.3032,
      "lng": 36.8856,
      "address": "Westlands, Nairobi"
    },
    "status": "requested",
    "fare": 450.0,
    "distance": 5.2,
    "duration": 15,
    "paymentStatus": "pending",
    "createdAt": "2024-01-15T10:30:00Z"
  }
}
```

### GET /trips
Get user's trips with pagination.

**Headers:** `Authorization: Bearer <token>`

**Query Parameters:**
- `page` (optional): Page number (default: 1)
- `limit` (optional): Items per page (default: 10)
- `status` (optional): Filter by status

**Response (200):**
```json
{
  "success": true,
  "data": {
    "trips": [
      {
        "id": "t_xyz789",
        "passengerId": "u_abc123",
        "driverId": "u_def456",
        "status": "completed",
        "fare": 450.0,
        "distance": 5.2,
        "duration": 15,
        "paymentStatus": "paid",
        "createdAt": "2024-01-15T10:30:00Z",
        "completedAt": "2024-01-15T11:00:00Z"
      }
    ],
    "pagination": {
      "page": 1,
      "limit": 10,
      "total": 25,
      "pages": 3
    }
  }
}
```

### GET /trips/available
Get available trips for drivers.

**Headers:** `Authorization: Bearer <token>` (Driver role required)

**Response (200):**
```json
{
  "success": true,
  "data": [
    {
      "id": "t_xyz789",
      "passengerId": "u_abc123",
      "pickup": {
        "lat": -1.2921,
        "lng": 36.8219,
        "address": "Nairobi CBD, Kenya"
      },
      "dropoff": {
        "lat": -1.3032,
        "lng": 36.8856,
        "address": "Westlands, Nairobi"
      },
      "status": "requested",
      "fare": 450.0,
      "distance": 5.2,
      "duration": 15,
      "createdAt": "2024-01-15T10:30:00Z"
    }
  ]
}
```

### PUT /trips/{trip_id}/accept
Driver accepts a trip request.

**Headers:** `Authorization: Bearer <token>` (Driver role required)

**Response (200):**
```json
{
  "success": true,
  "message": "Trip accepted",
  "data": {
    "id": "t_xyz789",
    "driverId": "u_def456",
    "status": "accepted",
    "acceptedAt": "2024-01-15T10:35:00Z"
  }
}
```

### PUT /trips/{trip_id}/complete
Complete a trip (Driver only).

**Headers:** `Authorization: Bearer <token>` (Driver role required)

**Response (200):**
```json
{
  "success": true,
  "message": "Trip completed",
  "data": {
    "id": "t_xyz789",
    "status": "completed",
    "paymentStatus": "paid",
    "completedAt": "2024-01-15T11:00:00Z"
  }
}
```

### POST /trips/{trip_id}/rate
Rate a completed trip (Passenger only).

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "rating": 5,
  "feedback": "Excellent service!"
}
```

**Response (200):**
```json
{
  "success": true,
  "message": "Rating submitted",
  "data": {
    "id": "t_xyz789",
    "rating": 5,
    "feedback": "Excellent service!"
  }
}
```

---

## 💳 Payment Endpoints

### POST /payments/initiate
Initiate M-Pesa STK Push payment.

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "tripId": "t_xyz789",
  "phone": "+254712345678",
  "amount": 450.0
}
```

**Response (200):**
```json
{
  "success": true,
  "message": "STK Push sent to your phone",
  "data": {
    "paymentId": "pay_abc123",
    "checkoutRequestId": "ws_CO_15012024103000123",
    "status": "pending",
    "responseDescription": "Success. Request accepted for processing"
  }
}
```

### GET /payments/status/{payment_id}
Check payment status.

**Headers:** `Authorization: Bearer <token>`

**Response (200):**
```json
{
  "success": true,
  "data": {
    "id": "pay_abc123",
    "tripId": "t_xyz789",
    "amount": 450.0,
    "phone": "+254712345678",
    "status": "paid",
    "mpesaReceiptNumber": "MPE123ABC456",
    "createdAt": "2024-01-15T10:45:00Z"
  }
}
```

### GET /payments
Get user's payment history.

**Headers:** `Authorization: Bearer <token>`

**Response (200):**
```json
{
  "success": true,
  "data": {
    "payments": [
      {
        "id": "pay_abc123",
        "tripId": "t_xyz789",
        "amount": 450.0,
        "status": "paid",
        "mpesaReceiptNumber": "MPE123ABC456",
        "createdAt": "2024-01-15T10:45:00Z"
      }
    ]
  }
}
```

---

## 🚛 Driver Endpoints

### GET /drivers/profile
Get driver profile information.

**Headers:** `Authorization: Bearer <token>` (Driver role required)

**Response (200):**
```json
{
  "success": true,
  "data": {
    "id": "d_def456",
    "userId": "u_def456",
    "name": "Jane Driver",
    "email": "jane@example.com",
    "phone": "+254798765432",
    "vehicle": {
      "make": "Toyota",
      "model": "Corolla",
      "year": 2020,
      "plate": "KCA 123A",
      "color": "White"
    },
    "documents": {
      "idCard": true,
      "license": true,
      "insurance": true,
      "logbook": false
    },
    "rating": 4.8,
    "totalTrips": 150,
    "totalEarnings": 75000.0,
    "status": "approved",
    "isOnline": true,
    "createdAt": "2024-01-01T00:00:00Z"
  }
}
```

### PUT /drivers/profile
Update driver profile information.

**Headers:** `Authorization: Bearer <token>` (Driver role required)

**Request Body:**
```json
{
  "vehicle": {
    "make": "Toyota",
    "model": "Corolla",
    "year": 2020,
    "plate": "KCA 123A",
    "color": "White"
  }
}
```

**Response (200):**
```json
{
  "success": true,
  "message": "Profile updated successfully",
  "data": {
    "vehicle": {
      "make": "Toyota",
      "model": "Corolla",
      "year": 2020,
      "plate": "KCA 123A",
      "color": "White"
    }
  }
}
```

### POST /drivers/upload-document
Upload driver KYC documents.

**Headers:** `Authorization: Bearer <token>` (Driver role required)

**Request:** Multipart form data
- `file`: Document file (PDF, PNG, JPG, JPEG - max 5MB)
- `type`: Document type (`idCard`, `license`, `insurance`, `logbook`)

**Response (200):**
```json
{
  "success": true,
  "message": "Document uploaded successfully",
  "data": {
    "type": "license",
    "uploaded": true
  }
}
```

### PUT /drivers/status
Update driver online status.

**Headers:** `Authorization: Bearer <token>` (Driver role required)

**Request Body:**
```json
{
  "isOnline": true
}
```

**Response (200):**
```json
{
  "success": true,
  "message": "Status updated",
  "data": {
    "isOnline": true
  }
}
```

### GET /drivers/earnings
Get driver earnings summary.

**Headers:** `Authorization: Bearer <token>` (Driver role required)

**Response (200):**
```json
{
  "success": true,
  "data": {
    "totalEarnings": 75000.0,
    "totalTrips": 150,
    "todayEarnings": 2500.0,
    "todayTrips": 5,
    "weekEarnings": 12000.0,
    "weekTrips": 24,
    "averagePerTrip": 500.0,
    "rating": 4.8
  }
}
```

---

## 👨‍💼 Admin Endpoints

### GET /admin/stats
Get system statistics (Admin only).

**Headers:** `Authorization: Bearer <token>` (Admin role required)

**Response (200):**
```json
{
  "success": true,
  "data": {
    "totalUsers": 1250,
    "totalDrivers": 320,
    "totalTrips": 5680,
    "totalRevenue": 2840000.0,
    "activeDrivers": 45,
    "pendingTrips": 12,
    "completedTripsToday": 89,
    "revenueToday": 44500.0
  }
}
```

### GET /admin/users/online
Get online users list (Admin only).

**Headers:** `Authorization: Bearer <token>` (Admin role required)

**Response (200):**
```json
{
  "success": true,
  "data": {
    "onlineDrivers": [
      {
        "id": "u_def456",
        "name": "Jane Driver",
        "email": "jane@example.com",
        "isOnline": true,
        "currentTrips": 1
      }
    ],
    "totalOnline": 45
  }
}
```

---

## 📊 Error Responses

All endpoints return standardized error responses:

**400 Bad Request:**
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Required field missing"
  }
}
```

**401 Unauthorized:**
```json
{
  "success": false,
  "error": {
    "code": "UNAUTHORIZED",
    "message": "Invalid or missing token"
  }
}
```

**403 Forbidden:**
```json
{
  "success": false,
  "error": {
    "code": "FORBIDDEN",
    "message": "Insufficient permissions"
  }
}
```

**404 Not Found:**
```json
{
  "success": false,
  "error": {
    "code": "NOT_FOUND",
    "message": "Resource not found"
  }
}
```

**500 Internal Server Error:**
```json
{
  "success": false,
  "error": {
    "code": "INTERNAL_ERROR",
    "message": "Internal server error"
  }
}
```

---

## 🔧 Rate Limiting & Best Practices

- **Rate Limit**: 100 requests per minute per IP
- **Token Expiry**: JWT tokens expire after 24 hours
- **File Upload**: Maximum 5MB per document
- **Phone Format**: Use international format (+254XXXXXXXXX)
- **Pagination**: Default limit is 10, maximum is 100

---

## 📱 SDK Examples

### JavaScript/Node.js
```javascript
const API_BASE = 'https://safedrive-backend-d579.onrender.com/api/v1';

// Login
const login = async (email, password) => {
  const response = await fetch(`${API_BASE}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password })
  });
  return response.json();
};

// Create Trip
const createTrip = async (token, tripData) => {
  const response = await fetch(`${API_BASE}/trips`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify(tripData)
  });
  return response.json();
};
```

### Python
```python
import requests

API_BASE = 'https://safedrive-backend-d579.onrender.com/api/v1'

# Login
def login(email, password):
    response = requests.post(f'{API_BASE}/auth/login', json={
        'email': email,
        'password': password
    })
    return response.json()

# Create Trip
def create_trip(token, trip_data):
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.post(f'{API_BASE}/trips', 
                           json=trip_data, headers=headers)
    return response.json()
```

---

## 🚀 Testing

Use the interactive Swagger UI at:
**https://safedrive-backend-d579.onrender.com/api/v1/docs/**

1. Click "Authorize" button
2. Enter: `Bearer <your_jwt_token>`
3. Test any endpoint with live data