# SafeDrive Backend - Development Guide

## Quick Start for Team Members

### **Setup (All Members)**
```bash
git clone https://github.com/koriMK/safedrive-backend.git
cd safedrive-backend
python -m venv venv
source venv/bin/activate  # Linux/Mac
# OR
venv\Scripts\activate     # Windows
pip install -r requirements.txt
```

### **Create Your Feature Branch**
```bash
# Member 1 (Auth)
git checkout -b feature/auth-improvements

# Member 2 (Driver)  
git checkout -b feature/driver-management

# Member 3 (Trip)
git checkout -b feature/trip-enhancements

# Member 4 (Payment)
git checkout -b feature/payment-integration
```

## File Ownership Matrix

| File/Directory | Primary Owner | Secondary | Purpose |
|---------------|---------------|-----------|---------|
| `routes/auth.py` | Member 1 | - | Authentication logic |
| `routes/users.py` | Member 1 | - | User management |
| `routes/drivers.py` | Member 2 | - | Driver operations |
| `routes/trips.py` | Member 3 | - | Trip management |
| `routes/payments.py` | Member 4 | - | Payment processing |
| `routes/admin.py` | Member 4 | Member 2 | Admin dashboard |
| `services/mpesa.py` | Member 4 | - | M-Pesa integration |
| `models.py` | All | - | Shared (coordinate changes) |
| `app.py` | All | Member 4 | Main app (coordinate changes) |
| `seed_config.py` | Member 1 | All | Database seeding |

## Development Rules

### **1. Model Changes**
- **MUST** coordinate with all team members
- Create migration scripts if needed
- Test with existing data
- Update `to_dict()` methods accordingly

### **2. API Changes**
- Follow existing response format
- Maintain backward compatibility
- Update documentation
- Add proper error handling

### **3. Database Schema**
- No direct schema changes without team approval
- Use SQLAlchemy migrations
- Test on sample data first

### **4. Code Standards**
```python
# Error Response Format (ALL endpoints)
{
    "success": False,
    "error": {
        "code": "ERROR_CODE",
        "message": "Human readable message"
    }
}

# Success Response Format (ALL endpoints)
{
    "success": True,
    "message": "Optional success message",
    "data": { ... }
}
```

## Testing Your Changes

### **Local Testing**
```bash
# Start local server
python app.py

# Test your endpoints
curl -X GET http://localhost:5002/api/v1/health
```

### **Integration Testing**
```bash
# Test with other team member's features
# Coordinate testing sessions
```

## Deployment Process

### **Member 4 Responsibilities:**
1. Merge approved PRs to main
2. Deploy to Render
3. Monitor deployment logs
4. Coordinate rollbacks if needed

### **All Members:**
1. Test locally before PR
2. Write clear commit messages
3. Update documentation
4. Notify team of breaking changes

## Communication Protocols

### **Daily Standups (15 min)**
- What did you work on yesterday?
- What will you work on today?
- Any blockers or dependencies?

### **Code Reviews**
- At least 1 team member must review
- Focus on your expertise area
- Check for integration issues
- Approve only if tested

### **Emergency Contacts**
- Production issues: Member 4
- Database issues: Member 1
- API issues: All coordinate
- Deployment issues: Member 4

## Common Issues & Solutions

### **Database Connection Issues**
```python
# Always use try/except for DB operations
try:
    db.session.commit()
except Exception as e:
    db.session.rollback()
    return error_response("DB_ERROR", str(e))
```

### **CORS Issues**
- Already configured in `app.py`
- Don't modify CORS settings without team approval

### **Authentication Issues**
- Use `@jwt_required()` decorator
- Check user roles with helper functions
- Member 1 handles auth-related bugs

### **Payment Integration Issues**
- Member 4 handles all M-Pesa related issues
- Test in sandbox mode first
- Never commit real credentials

## Git Workflow

```bash
# 1. Start feature
git checkout main
git pull origin main
git checkout -b feature/your-feature-name

# 2. Work on feature
git add .
git commit -m "feat: add user profile endpoint"

# 3. Push and create PR
git push origin feature/your-feature-name
# Create PR on GitHub

# 4. After approval and merge
git checkout main
git pull origin main
git branch -d feature/your-feature-name
```

## Environment Variables

### **Required for Local Development:**
```env
SECRET_KEY=your-local-secret-key
JWT_SECRET_KEY=your-local-jwt-key
DATABASE_URL=sqlite:///safedrive.db
```

### **Production (Render):**
- Member 4 manages production environment variables
- Never commit `.env` files
- Use `.env.example` for reference

## Support & Resources

- **Documentation:** This file + `README.md`
- **API Testing:** Use Postman/Insomnia
- **Database GUI:** DB Browser for SQLite
- **Code Editor:** VS Code recommended
- **Team Chat:** [Your team communication platform]

## Success Metrics

- **Code Quality:** All PRs reviewed and tested
- **Integration:** Features work together seamlessly  
- **Performance:** API responses under 2 seconds
- **Reliability:** 99% uptime on production
- **Team Velocity:** Complete sprints on time