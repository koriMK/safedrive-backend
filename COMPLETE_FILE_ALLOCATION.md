# SafeDrive Backend - Complete File Allocation by Team Member

## 📊 Equal Task Distribution Summary

| Member | Focus Area | Story Points | Primary Files | Secondary Files |
|--------|------------|--------------|---------------|-----------------|
| **Member 1** | Authentication & Users | 21 | `routes/auth.py`, `routes/users.py` | `models.py` (User model), `seed_config.py` (user functions) |
| **Member 2** | Driver Management | 24 | `routes/drivers.py`, `routes/admin.py` (driver sections) | `models.py` (Driver model), `utils/helpers.py` |
| **Member 3** | Trip Management | 27 | `routes/trips.py` | `models.py` (Trip model), trip algorithms |
| **Member 4** | Payments & Admin | 30 | `routes/payments.py`, `services/mpesa.py`, `routes/admin.py` (dashboard) | `models.py` (Payment & Config), deployment files |

---

## 📁 Complete File Allocation Matrix

### **🔐 Member 1: Authentication & User Management (21 points)**

#### **Primary Ownership (Full Control):**
- `routes/auth.py` - Authentication endpoints (register, login, profile)
- `routes/users.py` - User management endpoints
- `seed_config.py` - User seeding functions (admin, sample users)

#### **Secondary Ownership (Coordinate Changes):**
- `models.py` - User model (lines 7-40)
  - User class definition
  - Password hashing methods
  - User serialization (to_dict)
  - Online status tracking

#### **Files to Monitor:**
- `app.py` - JWT configuration
- `requirements.txt` - Auth-related dependencies

---

### **🚗 Member 2: Driver Management & Vehicle Operations (24 points)**

#### **Primary Ownership (Full Control):**
- `routes/drivers.py` - Driver profile, documents, status endpoints
- `utils/helpers.py` - Driver utility functions
- `uploads/` directory - Document storage (create if needed)

#### **Secondary Ownership (Coordinate Changes):**
- `routes/admin.py` - Driver approval sections (lines 85-150)
  - Driver listing endpoints
  - Approval/rejection workflows
  - Driver statistics
- `models.py` - Driver model (lines 42-95)
  - Driver class definition
  - Vehicle information
  - Driver statistics and ratings

#### **Files to Monitor:**
- `app.py` - File upload configuration
- `config.py` - Upload settings

---

### **🗺️ Member 3: Trip Management & Booking System (27 points)**

#### **Primary Ownership (Full Control):**
- `routes/trips.py` - All trip-related endpoints
  - Trip creation and management
  - Driver-passenger matching
  - Trip lifecycle (request → complete)
  - Rating system

#### **Secondary Ownership (Coordinate Changes):**
- `models.py` - Trip model (lines 97-170)
  - Trip class definition
  - Location handling
  - Status management
  - Trip serialization

#### **Files to Monitor:**
- `services/` - May need trip notification service
- `utils/helpers.py` - Geographic calculation functions

---

### **💳 Member 4: Payments, Admin & Infrastructure (30 points)**

#### **Primary Ownership (Full Control):**
- `routes/payments.py` - Payment processing endpoints
- `services/mpesa.py` - M-Pesa integration service
- `routes/admin.py` - Admin dashboard (except driver sections)
  - System statistics
  - Online user monitoring
  - Payment tracking

#### **Secondary Ownership (Coordinate Changes):**
- `models.py` - Payment & Config models (lines 172-270)
  - Payment class definition
  - Config management system
  - Configuration methods

#### **Infrastructure & Deployment Files:**
- `Procfile` - Process configuration
- `gunicorn.conf.py` - WSGI server configuration
- `runtime.txt` - Python version specification
- `render.yaml` - Render deployment configuration
- `.python-version` - Python version file
- `requirements.txt` - Dependency management coordination

---

## 📋 Shared Files (All Members Coordinate)

### **Core Application Files:**
- `app.py` - Flask application factory
  - **Coordinator:** Member 4 (infrastructure lead)
  - **Changes require:** All team approval
  - **Contains:** App configuration, blueprint registration, error handlers

- `models.py` - Database models
  - **Sections owned by:** Each member owns their model
  - **Changes require:** Team coordination
  - **Import coordination:** All members

- `requirements.txt` - Python dependencies
  - **Coordinator:** Member 4
  - **Process:** Members request additions via PR
  - **Review required:** Before adding new dependencies

### **Configuration Files:**
- `config.py` - Application configuration
- `.env.example` - Environment variables template
- `.env.production` - Production environment template

### **Documentation Files:**
- `README.md` - Project documentation
- `TEAM_ALLOCATION.md` - Team structure
- `DEVELOPMENT_GUIDE.md` - Development guidelines
- `JIRA_TASK_DIVISION.md` - Task breakdown
- `JIRA_TICKETS.md` - Ticket templates

### **Database & Testing:**
- `database.py` - Database utilities
- `seed_data.py` - Additional seeding
- `safedrive.db` - SQLite database file
- `test_backend.py` - Backend testing
- `verify_backend.py` - System verification

### **Utility & Support:**
- `utils/__init__.py` - Utils package initialization
- `routes/__init__.py` - Routes package initialization
- `services/__init__.py` - Services package initialization

---

## 🔄 File Change Coordination Protocol

### **Level 1: Independent Changes (No Coordination Needed)**
- Changes within your primary ownership files
- Bug fixes in your assigned sections
- Feature additions that don't affect other modules

### **Level 2: Team Notification (Slack/Discord Message)**
- Changes to shared utility functions
- New API endpoints that others might use
- Database model field additions

### **Level 3: Team Approval (PR Review Required)**
- Changes to `app.py` configuration
- New dependencies in `requirements.txt`
- Database model relationship changes
- Breaking API changes

### **Level 4: Team Meeting (All Members Present)**
- Major architectural changes
- Database schema migrations
- Deployment configuration changes
- Security-related modifications

---

## 📊 Workload Verification

### **File Count by Member:**
- **Member 1:** 3 primary + 2 secondary = 5 files
- **Member 2:** 3 primary + 3 secondary = 6 files  
- **Member 3:** 1 primary + 2 secondary = 3 files
- **Member 4:** 3 primary + 8 infrastructure = 11 files

### **Complexity Balance:**
- **Member 1:** Authentication complexity + user management
- **Member 2:** File uploads + admin workflows + driver logic
- **Member 3:** Geographic calculations + complex trip logic
- **Member 4:** Payment integration + system administration + deployment

### **Story Points Distribution:**
- **Member 1:** 21 points (Authentication foundation)
- **Member 2:** 24 points (Driver operations)
- **Member 3:** 27 points (Core trip functionality)
- **Member 4:** 30 points (Payments + infrastructure)

**Total:** 102 story points across 4 members = Balanced workload

---

## 🎯 Success Metrics by Member

### **Member 1 Success Criteria:**
- [ ] User registration/login working
- [ ] JWT authentication secure
- [ ] User profiles functional
- [ ] Admin user seeded properly

### **Member 2 Success Criteria:**
- [ ] Driver profiles complete
- [ ] Document upload working
- [ ] Driver approval workflow functional
- [ ] Vehicle information properly stored

### **Member 3 Success Criteria:**
- [ ] Trip creation working
- [ ] Driver-passenger matching functional
- [ ] Trip lifecycle complete
- [ ] Rating system operational

### **Member 4 Success Criteria:**
- [ ] M-Pesa payments working
- [ ] Payment safety measures active
- [ ] Admin dashboard functional
- [ ] System deployed and stable

This allocation ensures every file in the backend is assigned with clear ownership and coordination protocols.