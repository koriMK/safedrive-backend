#!/usr/bin/env python3
import requests
import json

BASE_URL = 'http://localhost:5002/api/v1'

def create_accounts():
    """Create test accounts for passenger, driver, and admin"""
    
    # Admin account
    admin_data = {
        'name': 'Admin User',
        'email': 'admin@safedrive.com',
        'password': 'admin123',
        'phone': '+254700000001',
        'role': 'admin'
    }
    
    # Passenger account
    passenger_data = {
        'name': 'John Passenger',
        'email': 'passenger@safedrive.com',
        'password': 'passenger123',
        'phone': '+254700000002',
        'role': 'passenger'
    }
    
    # Driver account
    driver_data = {
        'name': 'Mike Driver',
        'email': 'driver@safedrive.com',
        'password': 'driver123',
        'phone': '+254700000003',
        'role': 'driver'
    }
    
    accounts = [
        ('Admin', admin_data),
        ('Passenger', passenger_data),
        ('Driver', driver_data)
    ]
    
    created_users = {}
    
    for account_type, data in accounts:
        try:
            response = requests.post(f'{BASE_URL}/auth/register', json=data)
            if response.status_code == 201:
                result = response.json()
                created_users[account_type.lower()] = result['user']
                print(f"✓ {account_type} account created: {data['email']}")
            else:
                print(f"✗ Failed to create {account_type} account: {response.text}")
        except Exception as e:
            print(f"✗ Error creating {account_type} account: {e}")
    
    return created_users

def create_driver_profile(driver_user_id):
    """Create driver profile with vehicle information"""
    
    driver_profile = {
        'user_id': driver_user_id,
        'license_number': 'DL123456789',
        'vehicle': {
            'make': 'Toyota',
            'model': 'Corolla',
            'year': 2020,
            'plate': 'KCA 123A',
            'color': 'White'
        },
        'documents': {
            'license': 'license_doc.pdf',
            'insurance': 'insurance_doc.pdf',
            'vehicle_registration': 'registration_doc.pdf'
        }
    }
    
    try:
        response = requests.post(f'{BASE_URL}/drivers', json=driver_profile)
        if response.status_code == 201:
            print("✓ Driver profile created successfully")
            return response.json()
        else:
            print(f"✗ Failed to create driver profile: {response.text}")
    except Exception as e:
        print(f"✗ Error creating driver profile: {e}")
    
    return None

def approve_driver(driver_id):
    """Approve the driver account"""
    try:
        response = requests.put(f'{BASE_URL}/admin/drivers/{driver_id}/approve')
        if response.status_code == 200:
            print("✓ Driver approved successfully")
        else:
            print(f"✗ Failed to approve driver: {response.text}")
    except Exception as e:
        print(f"✗ Error approving driver: {e}")

def main():
    print("Creating SafeDrive test accounts...")
    print("=" * 50)
    
    # Create user accounts
    users = create_accounts()
    
    if 'driver' in users:
        print("\nCreating driver profile...")
        driver_profile = create_driver_profile(users['driver']['id'])
        
        if driver_profile:
            print("\nApproving driver...")
            approve_driver(driver_profile['driver']['id'])
    
    print("\n" + "=" * 50)
    print("Test accounts created successfully!")
    print("\nLogin credentials:")
    print("Admin: admin@safedrive.com / admin123")
    print("Passenger: passenger@safedrive.com / passenger123") 
    print("Driver: driver@safedrive.com / driver123")

if __name__ == '__main__':
    main()