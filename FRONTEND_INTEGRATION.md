# SafeDrive Frontend Integration Guide

## 🚀 Backend API Base URL
```javascript
const API_BASE_URL = 'https://safedrive-backend-d579.onrender.com/api/v1';
```

## 🔐 Authentication Endpoints

### **User Registration**
```javascript
// POST /api/v1/auth/register
const registerUser = async (userData) => {
  const response = await fetch(`${API_BASE_URL}/auth/register`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      name: userData.name,
      email: userData.email,
      phone: userData.phone, // Format: +254712345678
      password: userData.password,
      role: userData.role // 'passenger' or 'driver'
    })
  });
  
  const result = await response.json();
  if (result.success) {
    // Store token
    localStorage.setItem('token', result.token);
    localStorage.setItem('user', JSON.stringify(result.user));
  }
  return result;
};
```

### **User Login**
```javascript
// POST /api/v1/auth/login
const loginUser = async (email, password) => {
  const response = await fetch(`${API_BASE_URL}/auth/login`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ email, password })
  });
  
  const result = await response.json();
  if (result.success) {
    localStorage.setItem('token', result.token);
    localStorage.setItem('user', JSON.stringify(result.user));
  }
  return result;
};
```

### **Get Current User**
```javascript
// GET /api/v1/auth/me
const getCurrentUser = async () => {
  const token = localStorage.getItem('token');
  const response = await fetch(`${API_BASE_URL}/auth/me`, {
    headers: {
      'Authorization': `Bearer ${token}`,
    }
  });
  
  return await response.json();
};
```

## 🚗 Trip Management Endpoints

### **Create Trip Request**
```javascript
// POST /api/v1/trips
const createTrip = async (tripData) => {
  const token = localStorage.getItem('token');
  const response = await fetch(`${API_BASE_URL}/trips`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
    },
    body: JSON.stringify({
      pickup: {
        lat: tripData.pickupLat,
        lng: tripData.pickupLng,
        address: tripData.pickupAddress
      },
      dropoff: {
        lat: tripData.dropoffLat,
        lng: tripData.dropoffLng,
        address: tripData.dropoffAddress
      },
      notifyDrivers: true
    })
  });
  
  return await response.json();
};
```

### **Get Available Trips (For Drivers)**
```javascript
// GET /api/v1/trips/available
const getAvailableTrips = async () => {
  const token = localStorage.getItem('token');
  const response = await fetch(`${API_BASE_URL}/trips/available`, {
    headers: {
      'Authorization': `Bearer ${token}`,
    }
  });
  
  return await response.json();
};
```

### **Accept Trip (Driver)**
```javascript
// PUT /api/v1/trips/{tripId}/accept
const acceptTrip = async (tripId) => {
  const token = localStorage.getItem('token');
  const response = await fetch(`${API_BASE_URL}/trips/${tripId}/accept`, {
    method: 'PUT',
    headers: {
      'Authorization': `Bearer ${token}`,
    }
  });
  
  return await response.json();
};
```

## 💳 Payment Endpoints

### **Initiate M-Pesa Payment**
```javascript
// POST /api/v1/payments/initiate
const initiatePayment = async (tripId, phone, amount) => {
  const token = localStorage.getItem('token');
  const response = await fetch(`${API_BASE_URL}/payments/initiate`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
    },
    body: JSON.stringify({
      tripId,
      phone, // Format: +254712345678
      amount
    })
  });
  
  return await response.json();
};
```

### **Check Payment Status**
```javascript
// GET /api/v1/payments/status/{paymentId}
const checkPaymentStatus = async (paymentId) => {
  const token = localStorage.getItem('token');
  const response = await fetch(`${API_BASE_URL}/payments/status/${paymentId}`, {
    headers: {
      'Authorization': `Bearer ${token}`,
    }
  });
  
  return await response.json();
};
```

## 🛡️ Admin Endpoints

### **Get System Statistics**
```javascript
// GET /api/v1/admin/stats
const getAdminStats = async () => {
  const token = localStorage.getItem('token');
  const response = await fetch(`${API_BASE_URL}/admin/stats`, {
    headers: {
      'Authorization': `Bearer ${token}`,
    }
  });
  
  return await response.json();
};
```

### **Get All Users**
```javascript
// GET /api/v1/admin/users/online
const getAllUsers = async () => {
  const token = localStorage.getItem('token');
  const response = await fetch(`${API_BASE_URL}/admin/users/online`, {
    headers: {
      'Authorization': `Bearer ${token}`,
    }
  });
  
  return await response.json();
};
```

## 🔧 Utility Functions

### **API Helper with Error Handling**
```javascript
class SafeDriveAPI {
  constructor() {
    this.baseURL = 'https://safedrive-backend-d579.onrender.com/api/v1';
  }

  async request(endpoint, options = {}) {
    const token = localStorage.getItem('token');
    
    const config = {
      headers: {
        'Content-Type': 'application/json',
        ...(token && { 'Authorization': `Bearer ${token}` }),
        ...options.headers,
      },
      ...options,
    };

    try {
      const response = await fetch(`${this.baseURL}${endpoint}`, config);
      const data = await response.json();
      
      if (!data.success) {
        throw new Error(data.error?.message || 'Request failed');
      }
      
      return data;
    } catch (error) {
      console.error('API Error:', error);
      throw error;
    }
  }

  // Auth methods
  async register(userData) {
    return this.request('/auth/register', {
      method: 'POST',
      body: JSON.stringify(userData),
    });
  }

  async login(email, password) {
    return this.request('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    });
  }

  // Trip methods
  async createTrip(tripData) {
    return this.request('/trips', {
      method: 'POST',
      body: JSON.stringify(tripData),
    });
  }

  async getTrips() {
    return this.request('/trips');
  }

  // Payment methods
  async initiatePayment(paymentData) {
    return this.request('/payments/initiate', {
      method: 'POST',
      body: JSON.stringify(paymentData),
    });
  }
}

// Usage
const api = new SafeDriveAPI();
```

## 📱 React Integration Example

### **Authentication Context**
```javascript
import React, { createContext, useContext, useState, useEffect } from 'react';

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(localStorage.getItem('token'));
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (token) {
      // Verify token and get user data
      getCurrentUser()
        .then(result => {
          if (result.success) {
            setUser(result.data);
          } else {
            logout();
          }
        })
        .catch(() => logout())
        .finally(() => setLoading(false));
    } else {
      setLoading(false);
    }
  }, [token]);

  const login = async (email, password) => {
    const result = await loginUser(email, password);
    if (result.success) {
      setToken(result.token);
      setUser(result.user);
    }
    return result;
  };

  const logout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    setToken(null);
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, token, login, logout, loading }}>
      {children}
    </AuthContext.Provider>
  );
};
```

## 🚨 Error Handling

### **Standard Error Response Format**
```javascript
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Human readable error message"
  }
}
```

### **Common Error Codes**
- `MISSING_FIELD` - Required field missing
- `INVALID_EMAIL` - Email format invalid
- `INVALID_PHONE` - Phone number format invalid
- `EMAIL_EXISTS` - Email already registered
- `INVALID_CREDENTIALS` - Login failed
- `UNAUTHORIZED` - Invalid or missing token
- `TRIP_NOT_FOUND` - Trip doesn't exist
- `PAYMENT_FAILED` - Payment processing failed

## 🔄 Real-time Updates (Optional)

For real-time trip updates, consider implementing WebSocket connection or polling:

```javascript
// Polling example for trip status
const pollTripStatus = (tripId, callback) => {
  const interval = setInterval(async () => {
    try {
      const result = await api.request(`/trips/${tripId}`);
      if (result.success) {
        callback(result.data);
        
        // Stop polling if trip is completed
        if (result.data.status === 'completed') {
          clearInterval(interval);
        }
      }
    } catch (error) {
      console.error('Polling error:', error);
    }
  }, 5000); // Poll every 5 seconds

  return () => clearInterval(interval); // Cleanup function
};
```

This integration guide provides everything needed to connect your frontend to the SafeDrive backend API.(psycopg2.errors.UndefinedColumn) column users.is_online does not exist LINE 1: ...s.phone AS users_phone, users.role AS users_role, users.is_o... ^ [SQL: SELECT users.id AS users_id, users.email AS users_email, users.password_hash AS users_password_hash, users.name AS users_name, users.phone AS users_phone, users.role AS users_role, users.is_online AS users_is_online, users.last_seen AS users_last_seen, users.created_at AS users_created_at FROM users WHERE users.email = %(email_1)s LIMIT %(param_1)s] [parameters: {'email_1': 'passenger6@gmail.com', 'param_1': 1}] (Background on this error at: https://sqlalche.me/e/20/f405)