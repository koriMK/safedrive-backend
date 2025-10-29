# SafeDrive Backend - Team Allocation

## Team Structure (4 Members)

### **Member 1: Authentication & User Management Lead**
**Responsibility:** User authentication, registration, profile management

**Assigned Files:**
- `routes/auth.py` - Authentication endpoints (login, register, profile)
- `routes/users.py` - User management endpoints
- `models.py` - User model (lines 7-40)
- `seed_config.py` - User seeding functions

**Key Features:**
- JWT authentication system
- User registration/login
- Profile management
- Password security
- Role-based access control

---

### **Member 2: Driver Management & Vehicle Operations Lead**
**Responsibility:** Driver operations, vehicle management, driver approval

**Assigned Files:**
- `routes/drivers.py` - Driver-specific endpoints
- `routes/admin.py` - Driver approval and management (lines 85-150)
- `models.py` - Driver model (lines 42-95)
- Document upload functionality

**Key Features:**
- Driver registration and KYC
- Vehicle information management
- Driver approval workflow
- Online status tracking
- Driver statistics and ratings

---

### **Member 3: Trip Management & Booking System Lead**
**Responsibility:** Trip creation, matching, status management

**Assigned Files:**
- `routes/trips.py` - All trip-related endpoints
- `models.py` - Trip model (lines 97-170)
- Trip calculation algorithms
- Driver-passenger matching logic

**Key Features:**
- Trip request creation
- Fare calculation system
- Distance and duration estimation
- Trip status management
- Driver-passenger matching
- Trip rating system

---

### **Member 4: Payment Integration & Admin Dashboard Lead**
**Responsibility:** Payment processing, M-Pesa integration, admin features

**Assigned Files:**
- `routes/payments.py` - Payment processing endpoints
- `services/mpesa.py` - M-Pesa integration service
- `routes/admin.py` - Admin dashboard and statistics
- `models.py` - Payment and Config models (lines 172-220, 222-270)

**Key Features:**
- M-Pesa STK Push integration
- Payment status tracking
- Admin dashboard statistics
- System configuration management
- Revenue tracking
- Online user monitoring

---

## Shared Responsibilities

### **All Members:**
- `app.py` - Main application factory (coordinate changes)
- `models.py` - Database models (each member owns their section)
- `requirements.txt` - Dependencies (coordinate additions)
- Testing their respective modules
- Documentation for their features

### **Deployment & DevOps:**
- `Procfile`, `gunicorn.conf.py`, `runtime.txt` - **Member 4** (Payment Lead)
- `render.yaml` - **Member 4** (Payment Lead)
- Database migrations - **All members coordinate**

---

## Development Workflow

### **Branch Strategy:**
- `main` - Production branch
- `feature/auth-*` - Member 1 features
- `feature/driver-*` - Member 2 features  
- `feature/trip-*` - Member 3 features
- `feature/payment-*` - Member 4 features

### **Code Review Process:**
1. Each member creates feature branches
2. Pull requests require 1 other team member review
3. Member 4 handles final deployment coordination

### **Communication:**
- Daily standups to coordinate model changes
- Slack/Discord for quick questions
- Weekly sprint planning meetings
- Shared documentation in project README

---

## API Endpoint Ownership

### **Member 1 - Auth & Users:**
- `POST /api/v1/auth/register`
- `POST /api/v1/auth/login`
- `GET /api/v1/auth/me`
- `GET /api/v1/users/*`

### **Member 2 - Drivers:**
- `GET /api/v1/drivers/profile`
- `PUT /api/v1/drivers/profile`
- `POST /api/v1/drivers/upload-document`
- `PUT /api/v1/drivers/status`
- `GET /api/v1/admin/drivers`
- `PUT /api/v1/admin/drivers/{id}/approve`

### **Member 3 - Trips:**
- `POST /api/v1/trips`
- `GET /api/v1/trips`
- `GET /api/v1/trips/available`
- `PUT /api/v1/trips/{id}/accept`
- `PUT /api/v1/trips/{id}/complete`
- `POST /api/v1/trips/{id}/rate`

### **Member 4 - Payments & Admin:**
- `POST /api/v1/payments/initiate`
- `GET /api/v1/payments/status/{id}`
- `POST /api/v1/payments/callback`
- `GET /api/v1/admin/stats`
- `GET /api/v1/admin/users/online`
- `GET /api/v1/admin/trips`
- `GET /api/v1/admin/payments`

---

## Getting Started

1. **Clone Repository:** Each member clones the main repo
2. **Create Feature Branch:** Based on your assigned area
3. **Set Up Environment:** Follow README setup instructions
4. **Focus on Your Files:** Work primarily on your assigned files
5. **Coordinate Changes:** Discuss any shared file modifications
6. **Test Integration:** Ensure your features work with others
7. **Submit PR:** Request review from team members

## Contact Information

- **Team Lead:** [Member 4 - Payment & Admin Lead]
- **Technical Coordinator:** [Member 1 - Auth Lead]
- **QA Coordinator:** [Member 3 - Trip Lead]
- **Documentation Lead:** [Member 2 - Driver Lead]