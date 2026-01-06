"""
Test Helpers - Utility functions for tests
"""
import os
import sys
import django

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'edu_system.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()


def create_verified_user(username, email, password='SecurePass123!', role='student', **kwargs):
    """Create a user with email verified for testing"""
    user = User.objects.create_user(
        username=username,
        email=email,
        password=password,
        role=role,
        is_active=True,
        is_email_verified=True,
        first_name=kwargs.get('first_name', 'Test'),
        last_name=kwargs.get('last_name', 'User'),
        **{k: v for k, v in kwargs.items() if k not in ['first_name', 'last_name']}
    )
    return user


def create_verified_superuser(username, email, password='AdminPass123!', **kwargs):
    """Create a superuser with email verified for testing"""
    user = User.objects.create_superuser(
        username=username,
        email=email,
        password=password,
        first_name=kwargs.get('first_name', 'Admin'),
        last_name=kwargs.get('last_name', 'User'),
    )
    user.is_email_verified = True
    user.save()
    return user


class AuthenticatedTestCase:
    """Mixin for test cases that need authenticated users"""
    
    @classmethod
    def create_test_users(cls):
        """Create standard test users"""
        cls.teacher = create_verified_user(
            username='test_teacher',
            email='teacher@test.com',
            role='teacher',
            first_name='Test',
            last_name='Teacher'
        )
        cls.student = create_verified_user(
            username='test_student', 
            email='student@test.com',
            role='student',
            first_name='Test',
            last_name='Student'
        )
        cls.advisor = create_verified_user(
            username='test_advisor',
            email='advisor@test.com',
            role='advisor',
            first_name='Test',
            last_name='Advisor'
        )
        cls.admin = create_verified_superuser(
            username='test_admin',
            email='admin@test.com'
        )
    
    def login_user(self, email, password='SecurePass123!'):
        """Login and return JWT token"""
        response = self.client.post(
            '/api/user/login/',
            data={'email': email, 'password': password},
            content_type='application/json'
        )
        if response.status_code == 200:
            data = response.json()
            tokens = data.get('tokens', {})
            return tokens.get('access', data.get('token', ''))
        return ''
    
    def get_auth_header(self, token):
        """Return authorization header dict"""
        return {'HTTP_AUTHORIZATION': f'Bearer {token}'}
