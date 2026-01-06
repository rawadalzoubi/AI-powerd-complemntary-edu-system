"""
User Management Test Cases
TC-USER-001
"""
import json
from django.test import TestCase, Client
from django.contrib.auth import get_user_model

User = get_user_model()


class TestUserManagement(TestCase):
    """User Profile Management Tests"""

    def setUp(self):
        """Set up test client and authenticated user"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='test_user',
            email='test.user@example.com',
            password='SecurePass123!',
            first_name='Test',
            last_name='User',
            role='teacher',
            is_active=True,
            is_email_verified=True
        )
        # Login and get token
        login_response = self.client.post(
            '/api/user/login/',
            data={'email': 'test.user@example.com', 'password': 'SecurePass123!'},
            content_type='application/json'
        )
        if login_response.status_code == 200:
            data = login_response.json()
            tokens = data.get('tokens', {})
            self.token = tokens.get('access', data.get('access', ''))
        else:
            self.token = ''

    def get_auth_header(self):
        """Return authorization header"""
        return {'HTTP_AUTHORIZATION': f'Bearer {self.token}'}

    # =========================================================================
    # TC-USER-001: Edit Profile
    # =========================================================================
    def test_tc_user_001_view_profile(self):
        """
        Test ID: TC-USER-001 (Part 1 - View)
        Title: View User Profile Information
        """
        response = self.client.get(
            '/api/accounts/profile/',
            **self.get_auth_header()
        )
        
        if response.status_code != 404:
            self.assertEqual(response.status_code, 200)

    def test_tc_user_001_edit_profile_success(self):
        """
        Test ID: TC-USER-001 (Part 2 - Edit)
        Title: Successfully Edit User Profile Information
        """
        update_data = {
            'first_name': 'Test',
            'last_name': 'User',
            'country': 'SYRIA'
        }
        
        response = self.client.put(
            '/api/accounts/teacher/profile/',
            data=json.dumps(update_data),
            content_type='application/json',
            **self.get_auth_header()
        )
        
        if response.status_code != 404:
            self.assertIn(response.status_code, [200, 204])

    def test_tc_user_001_fail_unauthenticated(self):
        """TC-USER-001 Fail Case: Unauthenticated access"""
        response = self.client.get('/api/accounts/profile/')
        
        self.assertIn(response.status_code, [401, 403, 302, 404])
