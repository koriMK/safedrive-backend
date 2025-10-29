# SafeDrive Backend - Jira Task Division (4 Members)

## 📋 Epic: SafeDrive Backend Development

### **Member 1: Authentication & User Management**
**Jira Label:** `auth-team` | **Story Points:** 21

#### **Files Assigned:**
- `routes/auth.py` (Primary)
- `routes/users.py` (Primary)
- `models.py` (User model - lines 7-40)
- `seed_config.py` (User seeding functions)

#### **Jira Stories:**

**SAFE-101: User Registration System**
- **Description:** Implement user registration with email/phone validation
- **Acceptance Criteria:**
  - Email format validation
  - Phone number validation (Kenyan format)
  - Password strength requirements (configurable)
  - Role-based registration (passenger/driver/admin)
  - Duplicate email/phone prevention
- **Files:** `routes/auth.py` (register endpoint)
- **Story Points:** 8

**SAFE-102: Authentication System**
- **Description:** Implement JWT-based login system
- **Acceptance Criteria:**
  - Email/password login
  - JWT token generation
  - Password hashing with Werkzeug
  - Invalid credentials handling
- **Files:** `routes/auth.py` (login endpoint)
- **Story Points:** 5

**SAFE-103: User Profile Management**
- **Description:** User profile retrieval and online status tracking
- **Acceptance Criteria:**
  - Get current user profile
  - Update online status on access
  - Last seen timestamp tracking
  - Profile data serialization
- **Files:** `routes/auth.py` (me endpoint), `routes/users.py`
- **Story Points:** 5

**SAFE-104: User Data Seeding**
- **Description:** Create admin user and sample data
- **Acceptance Criteria:**
  - Default admin user creation
  - Sample user generation
  - Prevent duplicate seeding
  - Error handling for seed failures
- **Files:** `seed_config.py` (user functions)
- **Story Points:** 3

---

### **Member 2: Driver Management & Vehicle Operations**
**Jira Label:** `driver-team` | **Story Points:** 24

#### **Files Assigned:**
- `routes/drivers.py` (Primary)
- `routes/admin.py` (Driver approval sections)
- `models.py` (Driver model - lines 42-95)
- Document upload functionality

#### **Jira Stories:**

**SAFE-201: Driver Profile System**
- **Description:** Driver profile creation and management
- **Acceptance Criteria:**
  - Driver profile creation on registration
  - Vehicle information storage
  - Driver statistics tracking (rating, trips, earnings)
  - Profile update functionality
- **Files:** `routes/drivers.py`, `models.py` (Driver model)
- **Story Points:** 8

**SAFE-202: Driver Document Management**
- **Description:** KYC document upload and verification
- **Acceptance Criteria:**
  - Document upload endpoints
  - File validation and storage
  - Document status tracking
  - Secure file handling
- **Files:** `routes/drivers.py` (upload endpoints)
- **Story Points:** 6

**SAFE-203: Driver Status Management**
- **Description:** Online status and availability tracking
- **Acceptance Criteria:**
  - Online/offline status toggle
  - Availability for trip requests
  - Status persistence
  - Real-time status updates
- **Files:** `routes/drivers.py` (status endpoints)
- **Story Points:** 4

**SAFE-204: Driver Approval Workflow**
- **Description:** Admin driver approval system
- **Acceptance Criteria:**
  - Pending driver listing
  - Approve/reject functionality
  - Status change notifications
  - Approval history tracking
- **Files:** `routes/admin.py` (driver approval)
- **Story Points:** 6

---

### **Member 3: Trip Management & Booking System**
**Jira Label:** `trip-team` | **Story Points:** 27

#### **Files Assigned:**
- `routes/trips.py` (Primary)
- `models.py` (Trip model - lines 97-170)
- Trip calculation algorithms
- Driver-passenger matching logic

#### **Jira Stories:**

**SAFE-301: Trip Request System**
- **Description:** Passenger trip request creation
- **Acceptance Criteria:**
  - Pickup/dropoff location handling
  - Distance calculation (Haversine formula)
  - Fare calculation (configurable rates)
  - Duration estimation
  - Trip status management
- **Files:** `routes/trips.py` (create trip)
- **Story Points:** 10

**SAFE-302: Trip Matching & Assignment**
- **Description:** Driver-passenger matching system
- **Acceptance Criteria:**
  - Available trips for drivers
  - Trip acceptance by drivers
  - Driver assignment to trips
  - Prevent multiple assignments
  - Real-time trip updates
- **Files:** `routes/trips.py` (available, accept endpoints)
- **Story Points:** 8

**SAFE-303: Trip Lifecycle Management**
- **Description:** Trip status and completion workflow
- **Acceptance Criteria:**
  - Trip status transitions (requested → accepted → completed)
  - Trip completion by driver
  - Driver earnings update
  - Trip history tracking
  - Status validation
- **Files:** `routes/trips.py` (complete endpoint)
- **Story Points:** 6

**SAFE-304: Trip Rating System**
- **Description:** Post-trip rating and feedback
- **Acceptance Criteria:**
  - Passenger rating submission (1-5 stars)
  - Feedback text collection
  - Driver rating calculation
  - Rating history and averages
  - Rating validation
- **Files:** `routes/trips.py` (rate endpoint)
- **Story Points:** 3

---

### **Member 4: Payment Integration & Admin Dashboard**
**Jira Label:** `payment-admin-team` | **Story Points:** 30

#### **Files Assigned:**
- `routes/payments.py` (Primary)
- `services/mpesa.py` (Primary)
- `routes/admin.py` (Dashboard sections)
- `models.py` (Payment & Config models)
- Deployment files (`Procfile`, `gunicorn.conf.py`, etc.)

#### **Jira Stories:**

**SAFE-401: M-Pesa Integration**
- **Description:** M-Pesa STK Push payment system
- **Acceptance Criteria:**
  - STK Push initiation
  - Payment status tracking
  - Callback handling
  - Payment safety measures
  - Duplicate payment prevention
- **Files:** `services/mpesa.py`, `routes/payments.py`
- **Story Points:** 12

**SAFE-402: Payment Safety System**
- **Description:** Payment security and fraud prevention
- **Acceptance Criteria:**
  - Amount verification against trip fare
  - Duplicate payment blocking
  - Trip status validation for payments
  - Payment callback security
  - Error handling and rollbacks
- **Files:** `routes/payments.py` (safety checks)
- **Story Points:** 6

**SAFE-403: Admin Dashboard**
- **Description:** Administrative dashboard and statistics
- **Acceptance Criteria:**
  - System statistics (users, trips, revenue)
  - Online user monitoring
  - Driver management interface
  - Payment tracking
  - Real-time metrics
- **Files:** `routes/admin.py` (stats, online users)
- **Story Points:** 8

**SAFE-404: Configuration Management**
- **Description:** System configuration and deployment
- **Acceptance Criteria:**
  - Database configuration seeding
  - Environment-specific settings
  - Deployment configuration
  - Production optimization
  - Configuration API endpoints
- **Files:** `models.py` (Config), `seed_config.py`, deployment files
- **Story Points:** 4

---

## 🔄 Cross-Team Dependencies

### **Shared Responsibilities:**
- `models.py` - Coordinate model changes
- `app.py` - Coordinate application factory changes
- `requirements.txt` - Coordinate dependency additions
- Database migrations - All teams coordinate

### **Integration Points:**
1. **Auth ↔ Driver:** User creation triggers driver profile
2. **Driver ↔ Trip:** Driver availability affects trip matching
3. **Trip ↔ Payment:** Trip completion triggers payment
4. **All → Admin:** All modules feed into admin dashboard

---

## 📊 Sprint Planning (2-week sprints)

### **Sprint 1: Foundation**
- Member 1: SAFE-101, SAFE-102 (User registration & login)
- Member 2: SAFE-201 (Driver profiles)
- Member 3: SAFE-301 (Trip requests)
- Member 4: SAFE-404 (Configuration setup)

### **Sprint 2: Core Features**
- Member 1: SAFE-103, SAFE-104 (Profiles & seeding)
- Member 2: SAFE-202, SAFE-203 (Documents & status)
- Member 3: SAFE-302 (Trip matching)
- Member 4: SAFE-401 (M-Pesa integration)

### **Sprint 3: Advanced Features**
- Member 1: Testing & bug fixes
- Member 2: SAFE-204 (Driver approval)
- Member 3: SAFE-303, SAFE-304 (Trip completion & rating)
- Member 4: SAFE-402, SAFE-403 (Payment safety & admin)

---

## 🛠️ Development Workflow

### **Branch Strategy:**
- `main` - Production branch
- `develop` - Integration branch
- `feature/SAFE-XXX` - Individual story branches

### **Definition of Done:**
- [ ] Code implemented and tested
- [ ] Unit tests written (if applicable)
- [ ] Integration tested with other components
- [ ] Code reviewed by another team member
- [ ] Documentation updated
- [ ] Deployed to staging environment

### **Daily Standups:**
- What did you complete yesterday?
- What will you work on today?
- Any blockers or dependencies?
- Any model/API changes that affect others?

---

## 📞 Communication Channels

### **Team Leads:**
- **Technical Lead:** Member 4 (handles deployment)
- **Integration Lead:** Member 1 (coordinates auth dependencies)
- **QA Lead:** Member 3 (coordinates testing)
- **Documentation Lead:** Member 2 (maintains docs)

### **Escalation Path:**
1. Team member discussion
2. Team lead consultation
3. Full team meeting
4. Technical architect decision

---

## 🎯 Success Metrics

### **Individual Metrics:**
- Story points completed per sprint
- Code review participation
- Bug resolution time
- Documentation quality

### **Team Metrics:**
- Sprint velocity
- Integration success rate
- Production deployment frequency
- System uptime and performance

This division ensures equal workload distribution while maintaining clear ownership and accountability for each team member.