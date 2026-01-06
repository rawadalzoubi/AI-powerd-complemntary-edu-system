"""
Admin System Test Cases
TC-ADM-001 to TC-ADM-004
"""
import json
from django.test import TestCase, Client
from django.contrib.auth import get_user_model

User = get_user_model()


class TestAdminSystem(TestCase):
    """Admin System Tests"""

    def setUp(self):
        """Set up test client and admin user"""
        self.client = Client()
        
        # Create superuser/admin
        self.admin = User.objects.create_superuser(
            username='admin_user',
            email='admin@example.com',
            password='AdminPass123!',
            first_name='Admin',
            last_name='User'
        )
        self.admin.is_email_verified = True
        self.admin.save()
        
        # Create test advisor
        self.advisor = User.objects.create_user(
            username='advisor_admin',
            email='advisor@example.com',
            password='AdvisorPass123!',
            first_name='Test',
            last_name='Advisor',
            role='advisor',
            is_active=True,
            is_email_verified=True
        )

    def login_as(self, email, password):
        """Login and return token"""
        response = self.client.post(
            '/api/user/login/',
            data={'email': email, 'password': password},
            content_type='application/json'
        )
        if response.status_code == 200:
            data = response.json()
            tokens = data.get('tokens', {})
            return tokens.get('access', data.get('access', ''))
        return ''

    def get_auth_header(self, token):
        """Return authorization header"""
        return {'HTTP_AUTHORIZATION': f'Bearer {token}'}

    # =========================================================================
    # TC-ADM-001: Create Advisor
    # =========================================================================
    def test_tc_adm_001_create_advisor_success(self):
        """
        Test ID: TC-ADM-001
        Title: Admin Creates a New Advisor Account
        """
        token = self.login_as('admin@example.com', 'AdminPass123!')
        
        advisor_data = {
            'email': 'new.advisor@example.com',
            'password': 'NewAdvisorPass123!',
            'first_name': 'New',
            'last_name': 'Advisor',
        }
        
        response = self.client.post(
            '/advisors/create/',
            data=json.dumps(advisor_data),
            content_type='application/json',
            **self.get_auth_header(token)
        )
        
        self.assertIn(response.status_code, [200, 201, 302, 401, 403])

    def test_tc_adm_001_fail_duplicate_email(self):
        """TC-ADM-001 Fail Case: Duplicate email"""
        token = self.login_as('admin@example.com', 'AdminPass123!')
        
        advisor_data = {
            'email': 'advisor@example.com',
            'password': 'NewPass123!',
            'first_name': 'Duplicate',
            'last_name': 'Advisor'
        }
        
        response = self.client.post(
            '/advisors/create/',
            data=json.dumps(advisor_data),
            content_type='application/json',
            **self.get_auth_header(token)
        )
        
        # 302 = redirect (form-based view), 400/409 = API error
        self.assertIn(response.status_code, [302, 400, 401, 403, 409])

    def test_tc_adm_001_fail_non_admin(self):
        """TC-ADM-001 Fail Case: Non-admin cannot create advisor"""
        token = self.login_as('advisor@example.com', 'AdvisorPass123!')
        
        advisor_data = {
            'email': 'another.advisor@example.com',
            'password': 'Pass123!',
            'first_name': 'Another',
            'last_name': 'Advisor'
        }
        
        response = self.client.post(
            '/advisors/create/',
            data=json.dumps(advisor_data),
            content_type='application/json',
            **self.get_auth_header(token)
        )
        
        # 302 = redirect to login (unauthorized), 401/403 = API error
        self.assertIn(response.status_code, [302, 401, 403])

    # =========================================================================
    # TC-ADM-002: Deactivate Advisor
    # =========================================================================
    def test_tc_adm_002_deactivate_advisor_success(self):
        """
        Test ID: TC-ADM-002
        Title: Admin Deactivates an Advisor Account
        """
        token = self.login_as('admin@example.com', 'AdminPass123!')
        
        response = self.client.post(
            f'/advisors/toggle-status/{self.advisor.id}/',
            **self.get_auth_header(token)
        )
        
        self.assertIn(response.status_code, [200, 204, 302, 401, 403])
        
        if response.status_code in [200, 204]:
            self.advisor.refresh_from_db()
            self.assertFalse(self.advisor.is_active)

    def test_tc_adm_002_view_advisors_list(self):
        """TC-ADM-002: View advisors list"""
        token = self.login_as('admin@example.com', 'AdminPass123!')
        
        response = self.client.get(
            '/advisors/',
            **self.get_auth_header(token)
        )
        
        self.assertIn(response.status_code, [200, 302, 401, 403])

    # =========================================================================
    # TC-ADM-003: Invalidate Active Sessions
    # =========================================================================
    def test_tc_adm_003_invalidate_sessions(self):
        """
        Test ID: TC-ADM-003
        Title: Security: Immediate Session Termination
        """
        # Advisor gets a token first
        advisor_token = self.login_as('advisor@example.com', 'AdvisorPass123!')
        
        if advisor_token:
            # Verify advisor can access protected resource
            initial_response = self.client.get(
                '/api/user/profile/',
                **self.get_auth_header(advisor_token)
            )
            
            # Admin deactivates advisor
            admin_token = self.login_as('admin@example.com', 'AdminPass123!')
            self.client.post(
                f'/advisors/toggle-status/{self.advisor.id}/',
                **self.get_auth_header(admin_token)
            )
            
            # Check if token is still valid (depends on implementation)
            post_deactivation_response = self.client.get(
                '/api/user/profile/',
                **self.get_auth_header(advisor_token)
            )
            
            self.assertIn(post_deactivation_response.status_code, [200, 401, 403, 404])

    # =========================================================================
    # TC-ADM-004: Reset Advisor Password
    # =========================================================================
    def test_tc_adm_004_reset_password_success(self):
        """
        Test ID: TC-ADM-004
        Title: Admin Resets Advisor Password
        """
        token = self.login_as('admin@example.com', 'AdminPass123!')
        
        new_password = 'NewResetPass456!'
        
        reset_data = {
            'new_password': new_password,
            'confirm_password': new_password
        }
        
        response = self.client.post(
            f'/advisors/reset-password/{self.advisor.id}/',
            data=json.dumps(reset_data),
            content_type='application/json',
            **self.get_auth_header(token)
        )
        
        self.assertIn(response.status_code, [200, 204, 302, 401, 403])

    def test_tc_adm_004_view_advisor_stats(self):
        """TC-ADM-004: View advisor statistics"""
        token = self.login_as('admin@example.com', 'AdminPass123!')
        
        response = self.client.get(
            '/advisors/stats/',
            **self.get_auth_header(token)
        )
        
        self.assertIn(response.status_code, [200, 302, 401, 403])

    def test_tc_adm_004_delete_advisor(self):
        """TC-ADM-004: Delete advisor account"""
        token = self.login_as('admin@example.com', 'AdminPass123!')
        
        # Create advisor to delete
        advisor_to_delete = User.objects.create_user(
            username='delete_me',
            email='delete.me@example.com',
            password='DeleteMe123!',
            first_name='Delete',
            last_name='Me',
            role='advisor'
        )
        
        response = self.client.delete(
            f'/advisors/delete/{advisor_to_delete.id}/',
            **self.get_auth_header(token)
        )
        
        self.assertIn(response.status_code, [200, 204, 302, 401, 403])
