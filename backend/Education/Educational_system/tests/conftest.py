"""
Pytest Configuration and Shared Fixtures
"""
import os
import sys
import django

# Setup Django before importing models
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'edu_system.settings')
django.setup()

import pytest
from django.test import Client
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

User = get_user_model()


@pytest.fixture
def api_client():
    """Return DRF API test client"""
    return APIClient()


@pytest.fixture
def django_client():
    """Return Django test client"""
    return Client()


@pytest.fixture
def create_user():
    """Factory fixture to create users"""
    def _create_user(
        username,
        email,
        password='TestPass123!',
        role='student',
        is_active=True,
        **kwargs
    ):
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            role=role,
            is_active=is_active,
            **kwargs
        )
        # Mark email as verified for tests
        user.is_email_verified = True
        user.save()
        return user
    return _create_user


@pytest.fixture
def teacher_user(create_user):
    """Create a teacher user"""
    return create_user(
        username='teacher_fixture',
        email='teacher@test.com',
        role='teacher',
        first_name='Test',
        last_name='Teacher'
    )


@pytest.fixture
def student_user(create_user):
    """Create a student user"""
    return create_user(
        username='student_fixture',
        email='student@test.com',
        role='student',
        first_name='Test',
        last_name='Student'
    )


@pytest.fixture
def advisor_user(create_user):
    """Create an advisor user"""
    return create_user(
        username='advisor_fixture',
        email='advisor@test.com',
        role='advisor',
        first_name='Test',
        last_name='Advisor'
    )


@pytest.fixture
def admin_user():
    """Create a superuser/admin"""
    return User.objects.create_superuser(
        username='admin_fixture',
        email='admin@test.com',
        password='AdminPass123!',
        first_name='Admin',
        last_name='User'
    )


def get_auth_token(client, email, password):
    """Helper function to get JWT token"""
    response = client.post(
        '/api/user/login/',
        data={'email': email, 'password': password},
        content_type='application/json'
    )
    if response.status_code == 200:
        data = response.json()
        tokens = data.get('tokens', {})
        return tokens.get('access', data.get('access', ''))
    return ''


@pytest.fixture
def authenticated_client(api_client, student_user):
    """Return authenticated client with student user"""
    token = get_auth_token(api_client, 'student@test.com', 'TestPass123!')
    api_client.defaults['HTTP_AUTHORIZATION'] = f'Bearer {token}'
    return api_client


@pytest.fixture
def teacher_client(api_client, teacher_user):
    """Return authenticated client with teacher user"""
    token = get_auth_token(api_client, 'teacher@test.com', 'TestPass123!')
    api_client.defaults['HTTP_AUTHORIZATION'] = f'Bearer {token}'
    return api_client


@pytest.fixture
def advisor_client(api_client, advisor_user):
    """Return authenticated client with advisor user"""
    token = get_auth_token(api_client, 'advisor@test.com', 'TestPass123!')
    api_client.defaults['HTTP_AUTHORIZATION'] = f'Bearer {token}'
    return api_client


@pytest.fixture
def admin_client(api_client, admin_user):
    """Return authenticated client with admin user"""
    token = get_auth_token(api_client, 'admin@test.com', 'AdminPass123!')
    api_client.defaults['HTTP_AUTHORIZATION'] = f'Bearer {token}'
    return api_client
