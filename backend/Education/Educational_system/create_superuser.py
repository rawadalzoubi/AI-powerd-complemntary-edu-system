#!/usr/bin/env python
"""
Simple script to create a superuser with admin role
Usage: python create_superuser.py
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'edu_system.settings')
django.setup()

from django.contrib.auth import get_user_model
import getpass

User = get_user_model()

def create_superuser():
    print("🎓 EduTrack - Create Superuser")
    print("=" * 40)
    
    # Get user input
    email = input("Email: ")
    
    # Check if user exists
    if User.objects.filter(email=email).exists():
        print(f"❌ User with email '{email}' already exists!")
        return
    
    username = input("Username: ")
    
    # Check if username exists
    if User.objects.filter(username=username).exists():
        print(f"❌ User with username '{username}' already exists!")
        return
    
    first_name = input("First Name: ")
    last_name = input("Last Name: ")
    
    # Get password
    password = getpass.getpass("Password: ")
    password_confirm = getpass.getpass("Confirm Password: ")
    
    if password != password_confirm:
        print("❌ Passwords do not match!")
        return
    
    try:
        # Create superuser
        user = User.objects.create_user(
            email=email,
            username=username,
            first_name=first_name,
            last_name=last_name,
            password=password,
            role=User.ADMIN,  # Set admin role
            is_staff=True,
            is_superuser=True,
            is_active=True,
            is_email_verified=True
        )
        
        print(f"✅ Superuser '{username}' created successfully!")
        print(f"📧 Email: {email}")
        print(f"👤 Name: {first_name} {last_name}")
        print(f"🔧 Role: System Administrator")
        print(f"🎯 Access: http://localhost:8000/advisors/")
        
    except Exception as e:
        print(f"❌ Error creating superuser: {e}")

if __name__ == "__main__":
    create_superuser()