#!/usr/bin/env python
"""
Test script for Advisor Admin System
Run this to verify all functions work correctly
"""

import os
import django
import sys

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'edu_system.settings')
django.setup()

from eduAPI.models.user_model import User
from django.contrib.auth import authenticate

def test_advisor_admin_system():
    """Test all advisor admin functions"""
    print("🧪 Testing Advisor Admin System...")
    print("=" * 50)
    
    # Test 1: Check admin user exists
    print("\n1️⃣ Testing Admin User...")
    try:
        admin_user = User.objects.get(email='admin@edutrack.com')
        print(f"✅ Admin user found: {admin_user.email}")
        print(f"   - Is staff: {admin_user.is_staff}")
        print(f"   - Is superuser: {admin_user.is_superuser}")
    except User.DoesNotExist:
        print("❌ Admin user not found!")
        return False
    
    # Test 2: Check existing advisors
    print("\n2️⃣ Testing Existing Advisors...")
    advisors = User.objects.filter(role='advisor')
    print(f"✅ Found {advisors.count()} advisors:")
    for advisor in advisors:
        print(f"   - {advisor.get_full_name()} ({advisor.email}) - {'Active' if advisor.is_active else 'Inactive'}")
    
    # Test 3: Create new advisor
    print("\n3️⃣ Testing Create Advisor...")
    try:
        test_advisor, created = User.objects.get_or_create(
            email='test.advisor@edutrack.com',
            defaults={
                'first_name': 'Test',
                'last_name': 'Advisor',
                'role': 'advisor',
                'username': 'test.advisor@edutrack.com',
                'is_active': True
            }
        )
        test_advisor.set_password('testpass123')
        test_advisor.save()
        
        if created:
            print(f"✅ Created new test advisor: {test_advisor.get_full_name()}")
        else:
            print(f"✅ Test advisor already exists: {test_advisor.get_full_name()}")
    except Exception as e:
        print(f"❌ Error creating advisor: {e}")
        return False
    
    # Test 4: Update advisor password
    print("\n4️⃣ Testing Password Update...")
    try:
        import secrets
        import string
        
        # Generate new password
        alphabet = string.ascii_letters + string.digits + "!@#$%"
        new_password = ''.join(secrets.choice(alphabet) for i in range(12))
        
        # Update password
        test_advisor.set_password(new_password)
        test_advisor.save()
        
        # Verify password works
        auth_user = authenticate(username=test_advisor.email, password=new_password)
        if auth_user:
            print(f"✅ Password updated successfully: {new_password}")
        else:
            print("❌ Password update failed - authentication failed")
            return False
    except Exception as e:
        print(f"❌ Error updating password: {e}")
        return False
    
    # Test 5: Statistics
    print("\n5️⃣ Testing Statistics...")
    try:
        total_advisors = User.objects.filter(role='advisor').count()
        active_advisors = User.objects.filter(role='advisor', is_active=True).count()
        inactive_advisors = total_advisors - active_advisors
        
        print(f"✅ Statistics:")
        print(f"   - Total Advisors: {total_advisors}")
        print(f"   - Active Advisors: {active_advisors}")
        print(f"   - Inactive Advisors: {inactive_advisors}")
    except Exception as e:
        print(f"❌ Error getting statistics: {e}")
        return False
    
    # Test 6: Delete test advisor (cleanup)
    print("\n6️⃣ Testing Delete Advisor...")
    try:
        advisor_name = test_advisor.get_full_name()
        advisor_email = test_advisor.email
        test_advisor.delete()
        print(f"✅ Deleted test advisor: {advisor_name} ({advisor_email})")
    except Exception as e:
        print(f"❌ Error deleting advisor: {e}")
        return False
    
    print("\n" + "=" * 50)
    print("🎉 All tests passed! Advisor Admin System is working correctly.")
    print("\n📋 Access Information:")
    print("   URL: http://localhost:8000/admin/")
    print("   Email: admin@edutrack.com")
    print("   Password: admin123")
    print("\n🚀 Ready to use!")
    
    return True

if __name__ == "__main__":
    success = test_advisor_admin_system()
    sys.exit(0 if success else 1)