#!/usr/bin/env python
"""
Script to create admin user for EduTrack system
Usage: python create_admin.py
"""

import os
import django
import sys
from getpass import getpass

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'edu_system.settings')
django.setup()

from eduAPI.models.user_model import User

def create_admin_user():
    """Create or update admin user"""
    print("🔐 EduTrack Admin User Creation")
    print("=" * 40)
    
    # Get admin details
    email = input("Enter admin email (default: admin@edutrack.com): ").strip()
    if not email:
        email = "admin@edutrack.com"
    
    first_name = input("Enter first name (default: Admin): ").strip()
    if not first_name:
        first_name = "Admin"
    
    last_name = input("Enter last name (default: User): ").strip()
    if not last_name:
        last_name = "User"
    
    # Get password
    while True:
        password = getpass("Enter password (min 8 characters): ")
        if len(password) >= 8:
            confirm_password = getpass("Confirm password: ")
            if password == confirm_password:
                break
            else:
                print("❌ Passwords don't match. Try again.")
        else:
            print("❌ Password must be at least 8 characters long.")
    
    try:
        # Check if user exists
        try:
            admin_user = User.objects.get(email=email)
            print(f"📝 Updating existing admin user: {email}")
            created = False
        except User.DoesNotExist:
            print(f"➕ Creating new admin user: {email}")
            admin_user = User(email=email, username=email)
            created = True
        
        # Set user details
        admin_user.first_name = first_name
        admin_user.last_name = last_name
        admin_user.role = 'teacher'  # Use teacher role for admin
        admin_user.is_staff = True
        admin_user.is_superuser = True
        admin_user.is_active = True
        admin_user.set_password(password)
        admin_user.save()
        
        print(f"✅ Admin user {'created' if created else 'updated'} successfully!")
        print(f"📧 Email: {admin_user.email}")
        print(f"👤 Name: {admin_user.get_full_name()}")
        print(f"🔑 Password: [Hidden for security]")
        print(f"🌐 Admin URL: http://localhost:8000/admin/")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating admin user: {e}")
        return False

def show_existing_admins():
    """Show existing admin users"""
    print("\n📋 Existing Admin Users:")
    print("-" * 30)
    
    admins = User.objects.filter(is_staff=True, is_superuser=True)
    if admins.exists():
        for admin in admins:
            status = "✅ Active" if admin.is_active else "❌ Inactive"
            print(f"📧 {admin.email}")
            print(f"👤 {admin.get_full_name()}")
            print(f"📊 {status}")
            print(f"📅 Created: {admin.date_joined.strftime('%Y-%m-%d %H:%M')}")
            if admin.last_login:
                print(f"🕒 Last Login: {admin.last_login.strftime('%Y-%m-%d %H:%M')}")
            else:
                print("🕒 Last Login: Never")
            print("-" * 30)
    else:
        print("No admin users found.")

def main():
    """Main function"""
    print("🎓 EduTrack Admin Management")
    print("=" * 40)
    
    while True:
        print("\nChoose an option:")
        print("1. Create/Update Admin User")
        print("2. Show Existing Admins")
        print("3. Exit")
        
        choice = input("\nEnter your choice (1-3): ").strip()
        
        if choice == "1":
            create_admin_user()
        elif choice == "2":
            show_existing_admins()
        elif choice == "3":
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid choice. Please try again.")

if __name__ == "__main__":
    main()