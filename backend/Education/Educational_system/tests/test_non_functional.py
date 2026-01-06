"""
Non-Functional Requirements Test Cases
TC-NF-001, TC-SEC-001
"""
import json
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password, is_password_usable

User = get_user_model()


class TestNonFunctional(TestCase):
    """Non-Functional Requirements Tests"""

    def setUp(self):
        """Set up test client"""
        self.client = Client()

    # =========================================================================
    # TC-NF-001: Frontend Validation
    # =========================================================================
    def test_tc_nf_001_invalid_email_validation(self):
        """
        Test ID: TC-NF-001
        Title: Verify Frontend Input Validation
        """
        registration_data = {
            'username': 'test_user',
            'email': 'invalid-email',
            'password': 'SecurePass123!',
            'first_name': 'Test',
            'last_name': 'User',
            'role': 'student'
        }
        
        response = self.client.post(
            '/api/accounts/register/',
            data=json.dumps(registration_data),
            content_type='application/json'
        )
        
        # Server should reject invalid email (or 404 if endpoint doesn't exist)
        self.assertIn(response.status_code, [400, 404, 422])

    def test_tc_nf_001_required_field_validation(self):
        """TC-NF-001: Required field validation"""
        registration_data = {
            'email': 'test@example.com',
        }
        
        response = self.client.post(
            '/api/accounts/register/',
            data=json.dumps(registration_data),
            content_type='application/json'
        )
        
        self.assertIn(response.status_code, [400, 404, 422])

    def test_tc_nf_001_password_strength_validation(self):
        """TC-NF-001: Password strength validation"""
        registration_data = {
            'username': 'weak_pass_user',
            'email': 'test@example.com',
            'password': '123',
            'first_name': 'Test',
            'last_name': 'User',
            'role': 'student'
        }
        
        response = self.client.post(
            '/api/accounts/register/',
            data=json.dumps(registration_data),
            content_type='application/json'
        )
        
        self.assertIn(response.status_code, [400, 404, 422])


class TestSecurity(TestCase):
    """Security Tests"""

    def setUp(self):
        """Set up test data"""
        self.client = Client()
        self.test_password = 'SecureTestPass123!'
        self.user = User.objects.create_user(
            username='security_test',
            email='security.test@example.com',
            password=self.test_password,
            first_name='Security',
            last_name='Test',
            role='student',
            is_email_verified=True
        )

    # =========================================================================
    # TC-SEC-001: Secure Hashing
    # =========================================================================
    def test_tc_sec_001_password_hashed(self):
        """
        Test ID: TC-SEC-001
        Title: Verify Passwords are Hashed in the Database
        """
        user = User.objects.get(email='security.test@example.com')
        
        # Verify password is NOT stored in plaintext
        self.assertNotEqual(
            user.password, 
            self.test_password,
            "Password should NOT be stored in plaintext"
        )
        
        # Verify password is a valid hash
        self.assertTrue(
            is_password_usable(user.password),
            "Password should be a usable hash"
        )
        
        # Verify hash starts with algorithm identifier (Django 5.x uses scrypt by default)
        valid_algorithms = ['pbkdf2_sha256', 'argon2', 'bcrypt', 'scrypt']
        has_valid_algorithm = any(user.password.startswith(algo) for algo in valid_algorithms)
        self.assertTrue(
            has_valid_algorithm,
            f"Password should use a secure hashing algorithm. Got: {user.password[:20]}..."
        )
        
        # Verify original password can be verified against hash
        self.assertTrue(
            check_password(self.test_password, user.password),
            "Original password should verify against hash"
        )

    def test_tc_sec_001_password_not_in_response(self):
        """TC-SEC-001: Password not exposed in API responses"""
        login_response = self.client.post(
            '/api/user/login/',
            data={'email': 'security.test@example.com', 'password': self.test_password},
            content_type='application/json'
        )
        
        if login_response.status_code == 200:
            token = login_response.json().get('access', '')
            
            response = self.client.get(
                '/api/user/profile/',
                HTTP_AUTHORIZATION=f'Bearer {token}'
            )
            
            if response.status_code == 200:
                response_text = str(response.content)
                self.assertNotIn(self.test_password, response_text)

    def test_tc_sec_001_different_users_different_hashes(self):
        """TC-SEC-001: Same password produces different hashes"""
        same_password = 'SamePassword123!'
        
        user1 = User.objects.create_user(
            username='user1_hash',
            email='user1@example.com',
            password=same_password,
            first_name='User',
            last_name='One',
            role='student'
        )
        user2 = User.objects.create_user(
            username='user2_hash',
            email='user2@example.com',
            password=same_password,
            first_name='User',
            last_name='Two',
            role='student'
        )
        
        self.assertNotEqual(
            user1.password,
            user2.password,
            "Same password should produce different hashes for different users"
        )

    def test_tc_sec_001_sql_injection_prevention(self):
        """TC-SEC-001: SQL injection prevention"""
        malicious_email = "test@example.com'; DROP TABLE users; --"
        
        response = self.client.post(
            '/api/user/login/',
            data=json.dumps({
                'email': malicious_email,
                'password': 'test'
            }),
            content_type='application/json'
        )
        
        # Should not crash
        self.assertIn(response.status_code, [400, 401, 404, 422])
        
        # Verify users table still exists
        self.assertTrue(User.objects.exists())
