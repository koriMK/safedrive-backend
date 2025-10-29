#!/usr/bin/env python3
"""
Backend Verification Script
Tests SQLAlchemy ORM functionality and seeding
"""

from app import create_app
from models import db, User, Driver, Trip, Payment, Config
from seed_config import run_seeds

def verify_database_setup():
    """Verify database tables and relationships"""
    print("🔍 Verifying Database Setup...")
    
    app = create_app()
    with app.app_context():
        try:
            # Check if tables exist by querying models
            models_to_check = [
                ('users', User),
                ('drivers', Driver), 
                ('trips', Trip),
                ('payments', Payment),
                ('config', Config)
            ]
            
            for table_name, model in models_to_check:
                try:
                    model.query.count()
                    print(f"✅ Table '{table_name}' exists and accessible")
                except Exception:
                    print(f"❌ Table '{table_name}' missing or inaccessible")
                    return False
            
            return True
        except Exception as e:
            print(f"❌ Database setup error: {e}")
            return False

def verify_seeding():
    """Verify seeding functionality"""
    print("\n🌱 Verifying Seeding...")
    
    app = create_app()
    with app.app_context():
        try:
            # Check config seeding
            config_count = Config.query.count()
            print(f"✅ Config entries: {config_count}")
            
            # Check admin user
            admin = User.query.filter_by(role='admin').first()
            if admin:
                print(f"✅ Admin user: {admin.email}")
            else:
                print("❌ Admin user not found")
            
            # Check sample drivers
            drivers = Driver.query.filter_by(status='approved').count()
            print(f"✅ Sample drivers: {drivers}")
            
            # Test config retrieval
            app_name = Config.get_value('APP_NAME', 'Unknown')
            print(f"✅ Config retrieval works: APP_NAME = {app_name}")
            
            return True
        except Exception as e:
            print(f"❌ Seeding verification error: {e}")
            return False

def verify_orm_operations():
    """Verify ORM CRUD operations"""
    print("\n🔧 Verifying ORM Operations...")
    
    app = create_app()
    with app.app_context():
        try:
            # Test user creation
            test_user = User(
                email='test@example.com',
                name='Test User',
                phone='+254700000001',
                role='passenger'
            )
            test_user.set_password('testpass123')
            
            db.session.add(test_user)
            db.session.commit()
            print("✅ User creation works")
            
            # Test user retrieval
            retrieved_user = User.query.filter_by(email='test@example.com').first()
            if retrieved_user and retrieved_user.check_password('testpass123'):
                print("✅ User retrieval and password check works")
            else:
                print("❌ User retrieval failed")
                return False
            
            # Test relationships
            if retrieved_user.role == 'passenger':
                print("✅ User attributes work")
            
            # Test to_dict method
            user_dict = retrieved_user.to_dict()
            if 'id' in user_dict and 'email' in user_dict:
                print("✅ to_dict() serialization works")
            else:
                print("❌ to_dict() serialization failed")
                return False
            
            # Cleanup test data
            db.session.delete(retrieved_user)
            db.session.commit()
            print("✅ User deletion works")
            
            return True
        except Exception as e:
            print(f"❌ ORM operations error: {e}")
            return False

def verify_config_system():
    """Verify configuration system"""
    print("\n⚙️ Verifying Config System...")
    
    app = create_app()
    with app.app_context():
        try:
            # Test config get/set
            Config.set_value('TEST_KEY', 'test_value', 'Test configuration')
            retrieved_value = Config.get_value('TEST_KEY')
            
            if retrieved_value == 'test_value':
                print("✅ Config set/get works")
            else:
                print("❌ Config set/get failed")
                return False
            
            # Test default values
            default_value = Config.get_value('NON_EXISTENT_KEY', 'default')
            if default_value == 'default':
                print("✅ Config default values work")
            else:
                print("❌ Config default values failed")
                return False
            
            # Cleanup test config
            test_config = Config.query.filter_by(key='TEST_KEY').first()
            if test_config:
                db.session.delete(test_config)
                db.session.commit()
            
            return True
        except Exception as e:
            print(f"❌ Config system error: {e}")
            return False

def main():
    """Run all verification tests"""
    print("🚀 SafeDrive Backend Verification")
    print("=" * 40)
    
    tests = [
        verify_database_setup,
        verify_seeding,
        verify_orm_operations,
        verify_config_system
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        else:
            break
    
    print("\n" + "=" * 40)
    print(f"📊 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Backend is working correctly.")
        return True
    else:
        print("❌ Some tests failed. Check the errors above.")
        return False

if __name__ == '__main__':
    main()