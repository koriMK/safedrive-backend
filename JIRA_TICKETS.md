# SafeDrive Backend - Jira Ticket Templates

## 🎫 Ready-to-Import Jira Tickets

### **MEMBER 1 TICKETS (Authentication Team)**

---

**Ticket ID:** SAFE-101  
**Title:** User Registration System  
**Type:** Story  
**Priority:** High  
**Story Points:** 8  
**Assignee:** Member 1  
**Labels:** auth-team, backend, registration  

**Description:**
Implement comprehensive user registration system with validation and role management.

**Acceptance Criteria:**
- [ ] Email format validation using regex
- [ ] Kenyan phone number validation (+254 format)
- [ ] Configurable password strength requirements
- [ ] Support for passenger/driver/admin roles
- [ ] Prevent duplicate email/phone registration
- [ ] Return appropriate error messages for validation failures
- [ ] Generate JWT token on successful registration

**Technical Requirements:**
- Use Werkzeug for password hashing
- Implement email/phone uniqueness checks
- Create driver profile automatically for driver role
- Follow existing API response format

**Files to Modify:**
- `routes/auth.py` (register endpoint)
- `models.py` (User model validation)

---

**Ticket ID:** SAFE-102  
**Title:** JWT Authentication System  
**Type:** Story  
**Priority:** High  
**Story Points:** 5  
**Assignee:** Member 1  
**Labels:** auth-team, backend, jwt, security  

**Description:**
Implement secure JWT-based authentication system for user login.

**Acceptance Criteria:**
- [ ] Email/password login validation
- [ ] JWT token generation with configurable expiry
- [ ] Secure password verification
- [ ] Handle invalid credentials gracefully
- [ ] Return user profile data with token
- [ ] Implement token refresh mechanism

**Technical Requirements:**
- Use Flask-JWT-Extended
- Implement proper error handling
- Follow security best practices
- Maintain session state

**Files to Modify:**
- `routes/auth.py` (login endpoint)

---

### **MEMBER 2 TICKETS (Driver Management Team)**

---

**Ticket ID:** SAFE-201  
**Title:** Driver Profile Management System  
**Type:** Story  
**Priority:** High  
**Story Points:** 8  
**Assignee:** Member 2  
**Labels:** driver-team, backend, profiles  

**Description:**
Create comprehensive driver profile system with vehicle information and statistics.

**Acceptance Criteria:**
- [ ] Automatic driver profile creation on driver registration
- [ ] Vehicle information storage (make, model, year, plate, color)
- [ ] Driver statistics tracking (rating, total trips, earnings)
- [ ] Profile update endpoints
- [ ] Data validation for vehicle information
- [ ] Profile retrieval with user relationship

**Technical Requirements:**
- Implement proper foreign key relationships
- Use SQLAlchemy ORM for data operations
- Implement data serialization methods
- Handle profile updates safely

**Files to Modify:**
- `routes/drivers.py` (profile endpoints)
- `models.py` (Driver model)

---

**Ticket ID:** SAFE-202  
**Title:** Driver Document Upload System  
**Type:** Story  
**Priority:** Medium  
**Story Points:** 6  
**Assignee:** Member 2  
**Labels:** driver-team, backend, documents, kyc  

**Description:**
Implement secure document upload system for driver KYC verification.

**Acceptance Criteria:**
- [ ] File upload endpoints for ID, license, insurance, logbook
- [ ] File type validation (images, PDFs)
- [ ] File size limits and security checks
- [ ] Document status tracking
- [ ] Secure file storage
- [ ] Document retrieval endpoints

**Technical Requirements:**
- Use Werkzeug for file handling
- Implement file validation
- Store file paths securely
- Handle upload errors gracefully

**Files to Modify:**
- `routes/drivers.py` (upload endpoints)

---

### **MEMBER 3 TICKETS (Trip Management Team)**

---

**Ticket ID:** SAFE-301  
**Title:** Trip Request Creation System  
**Type:** Story  
**Priority:** High  
**Story Points:** 10  
**Assignee:** Member 3  
**Labels:** trip-team, backend, booking  

**Description:**
Implement trip request system with location handling and fare calculation.

**Acceptance Criteria:**
- [ ] Pickup/dropoff location validation
- [ ] Distance calculation using Haversine formula
- [ ] Configurable fare calculation (base fare + rate per km)
- [ ] Duration estimation based on average speed
- [ ] Trip creation with proper status
- [ ] Location coordinate validation
- [ ] Integration with driver notification system

**Technical Requirements:**
- Use Config model for pricing parameters
- Implement geographic calculations
- Validate coordinate ranges
- Handle calculation errors

**Files to Modify:**
- `routes/trips.py` (create trip endpoint)
- `models.py` (Trip model)

---

**Ticket ID:** SAFE-302  
**Title:** Driver-Passenger Matching System  
**Type:** Story  
**Priority:** High  
**Story Points:** 8  
**Assignee:** Member 3  
**Labels:** trip-team, backend, matching  

**Description:**
Implement trip matching system allowing drivers to view and accept available trips.

**Acceptance Criteria:**
- [ ] Available trips endpoint for drivers
- [ ] Trip acceptance by drivers
- [ ] Prevent multiple driver assignments
- [ ] Real-time trip status updates
- [ ] Driver authorization validation
- [ ] Trip assignment timestamps

**Technical Requirements:**
- Implement proper locking mechanisms
- Validate driver eligibility
- Update trip status atomically
- Handle concurrent access

**Files to Modify:**
- `routes/trips.py` (available, accept endpoints)

---

### **MEMBER 4 TICKETS (Payment & Admin Team)**

---

**Ticket ID:** SAFE-401  
**Title:** M-Pesa STK Push Integration  
**Type:** Story  
**Priority:** High  
**Story Points:** 12  
**Assignee:** Member 4  
**Labels:** payment-team, backend, mpesa, integration  

**Description:**
Integrate M-Pesa STK Push for seamless mobile payments.

**Acceptance Criteria:**
- [ ] STK Push initiation with trip details
- [ ] Payment status tracking and updates
- [ ] Callback handling for payment confirmation
- [ ] Phone number format validation
- [ ] Payment amount verification
- [ ] Error handling for failed payments
- [ ] Payment receipt generation

**Technical Requirements:**
- Use Daraja API for M-Pesa integration
- Implement OAuth token management
- Handle callback security
- Store payment records

**Files to Modify:**
- `services/mpesa.py` (M-Pesa service)
- `routes/payments.py` (payment endpoints)

---

**Ticket ID:** SAFE-402  
**Title:** Payment Security & Safety System  
**Type:** Story  
**Priority:** High  
**Story Points:** 6  
**Assignee:** Member 4  
**Labels:** payment-team, backend, security, safety  

**Description:**
Implement comprehensive payment safety measures to protect users from fraud.

**Acceptance Criteria:**
- [ ] Duplicate payment prevention
- [ ] Amount verification against trip fare
- [ ] Trip status validation before payment
- [ ] Payment callback security
- [ ] Double processing prevention
- [ ] Automatic rollback on failures
- [ ] Payment audit trail

**Technical Requirements:**
- Implement database transactions
- Add payment validation layers
- Handle edge cases and errors
- Maintain data consistency

**Files to Modify:**
- `routes/payments.py` (safety checks)

---

## 📋 Jira Import Instructions

### **Step 1: Create Epic**
```
Epic Name: SafeDrive Backend Development
Epic Key: SAFE-EPIC-1
Description: Complete backend development for SafeDrive ride-sharing platform
```

### **Step 2: Import Stories**
1. Copy each ticket template above
2. Create new story in Jira
3. Fill in all fields as specified
4. Link to Epic: SAFE-EPIC-1
5. Assign to respective team member

### **Step 3: Create Sprint Structure**
```
Sprint 1: Foundation (SAFE-101, SAFE-102, SAFE-201, SAFE-301, SAFE-404)
Sprint 2: Core Features (SAFE-103, SAFE-104, SAFE-202, SAFE-203, SAFE-302, SAFE-401)
Sprint 3: Advanced Features (SAFE-204, SAFE-303, SAFE-304, SAFE-402, SAFE-403)
```

### **Step 4: Set Up Board**
- Create Kanban board with columns: To Do, In Progress, Code Review, Testing, Done
- Add swimlanes by assignee
- Configure filters by labels (auth-team, driver-team, trip-team, payment-admin-team)

This structure provides clear, actionable tickets with equal workload distribution across all team members.