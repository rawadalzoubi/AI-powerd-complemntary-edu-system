#!/usr/bin/env python
"""
Simple script to delete superuser accounts
Usage: python delete_superuser.py
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'edu_system.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

def list_superusers():
    """List all superuser accounts"""
    superusers = User.objects.filter(is_superuser=True)
    
    if not superusers.exists():
        print("❌ No superusers found.")
        return []
    
    print("\n🔧 Current Superusers:")
    print("=" * 50)
    
    for i, user in enumerate(superusers, 1):
        print(f"{i}. ID: {user.id} | Username: {user.username} | Email: {user.email} | Role: {user.role}")
    
    return list(superusers)

def delete_superuser():
    print("🗑️  EduTrack - Delete Superuser")
    print("=" * 40)
    
    # List current superusers
    superusers = list_superusers()
    
    if not superusers:
        return
    
    print("\nOptions:")
    print("1. Delete by email")
    print("2. Delete by username") 
    print("3. Delete by selecting from list")
    print("4. Delete ALL superusers (⚠️  DANGEROUS!)")
    print("0. Cancel")
    
    choice = input("\nEnter your choice (0-4): ").strip()
    
    if choice == "0":
        print("❌ Operation cancelled.")
        return
    
    elif choice == "1":
        email = input("Enter email: ").strip()
        delete_by_email(email)
    
    elif choice == "2":
        username = input("Enter username: ").strip()
        delete_by_username(username)
    
    elif choice == "3":
        delete_by_selection(superusers)
    
    elif choice == "4":
        delete_all_superusers(superusers)
    
    else:
        print("❌ Invalid choice.")

def delete_by_email(email):
    try:
        user = User.objects.get(email=email, is_superuser=True)
        confirm = input(f"Delete superuser '{user.username}' ({email})? (y/N): ").strip().lower()
        
        if confirm == 'y':
            user.delete()
            print(f"✅ Superuser '{user.username}' deleted successfully!")
        else:
            print("❌ Operation cancelled.")
    except User.DoesNotExist:
        print(f"❌ Superuser with email '{email}' not found.")

def delete_by_username(username):
    try:
        user = User.objects.get(username=username, is_superuser=True)
        confirm = input(f"Delete superuser '{username}' ({user.email})? (y/N): ").strip().lower()
        
        if confirm == 'y':
            user.delete()
            print(f"✅ Superuser '{username}' deleted successfully!")
        else:
            print("❌ Operation cancelled.")
    except User.DoesNotExist:
        print(f"❌ Superuser with username '{username}' not found.")

def delete_by_selection(superusers):
    try:
        choice = int(input(f"\nSelect superuser to delete (1-{len(superusers)}): "))
        
        if 1 <= choice <= len(superusers):
            user = superusers[choice - 1]
            confirm = input(f"Delete superuser '{user.username}' ({user.email})? (y/N): ").strip().lower()
            
            if confirm == 'y':
                user.delete()
                print(f"✅ Superuser '{user.username}' deleted successfully!")
            else:
                print("❌ Operation cancelled.")
        else:
            print("❌ Invalid selection.")
    except ValueError:
        print("❌ Please enter a valid number.")

def delete_all_superusers(superusers):
    print("\n⚠️  WARNING: This will delete ALL superuser accounts!")
    print("Accounts to be deleted:")
    
    for user in superusers:
        print(f"- {user.username} ({user.email})")
    
    confirm = input('\nType "DELETE ALL" to confirm: ').strip()
    
    if confirm == "DELETE ALL":
        count = len(superusers)
        User.objects.filter(is_superuser=True).delete()
        print(f"✅ Deleted {count} superuser account(s)!")
    else:
        print("❌ Operation cancelled.")

if __name__ == "__main__":
    delete_superuser()