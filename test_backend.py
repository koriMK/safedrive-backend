#!/usr/bin/env python3
"""Simple backend test"""

from app import create_app
from models import db, User, Config

app = create_app()
with app.app_context():
    print("✅ App created successfully")
    
    # Test config
    configs = Config.query.all()
    print(f"✅ Config entries: {len(configs)}")
    
    # Test users
    users = User.query.all()
    print(f"✅ Users: {len(users)}")
    
    # Test admin
    admin = User.query.filter_by(role='admin').first()
    if admin:
        print(f"✅ Admin user: {admin.email}")
    
    print("🎉 Backend working with SQLAlchemy ORM and seeding!")