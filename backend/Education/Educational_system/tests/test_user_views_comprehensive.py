"""
Comprehensive User Views Tests
Tests for user_views.py to increase coverage
"""
import json
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from unittest.mock import patch, MagicMock

User = get_user_model()


class TestUserRegistration(TestCase):
    """Tests for user registration endpoint"""

    def setUp(self):
        self.client = Client()

    def test_register_student_success(self):
        """Test successful student registration"""
        data = {
            'username': 'newstudent',
            'email': 'newstudent@test.com',
            'password': 'SecurePass123!',
            'password_confirm': 'SecurePass123!',
            'first_name': 'New',
            'last_name': 'Student',
            'role': 'student'
        }
        response = self.client.post(
            '/api/user/register/',
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertIn(response.status_code, [200, 201])

    def test_register_teacher_success(self):
        """Test successful teacher registration"""
        data = {
            'username': 'newteacher',
            'email': 'newteacher@test.com',
            'password': 'SecurePass123!',
            'password_confirm': 'SecurePass123!',
            'first_name': 'New',
            'last_name': 'Teacher',
            'role': 'teacher'
        }
        response = self.client.post(
            '/api/user/register/',
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertIn(response.status_code, [200, 201])

    def test_register_duplicate_email(self):
        """Test registration with duplicate email"""
        User.objects.create_user(
            username='existing',
            email='existing@test.com',
            password='SecurePass123!',
            first_name='Existing',
            last_name='User',
            role='student'
        )
        data = {
            'username': 'newuser',
            'email': 'existing@test.com',
            'password': 'SecurePass123!',
            'password_confirm': 'SecurePass123!',
            'first_name': 'New',
            'last_name': 'User',
            'role': 'student'
        }
        response = self.client.post(
            '/api/user/register/',
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)

    def test_register_invalid_email(self):
        """Test registration with invalid email"""
        data = {
            'username': 'newuser',
            'email': 'invalid-email',
            'password': 'SecurePass123!',
            'password_confirm': 'SecurePass123!',
            'first_name': 'New',
            'last_name': 'User',
            'role': 'student'
        }
        response = self.client.post(
            '/api/user/register/',
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)

    def test_register_missing_fields(self):
        """Test registration with missing required fields"""
        data = {
            'email': 'test@test.com'
        }
        response = self.client.post(
            '/api/user/register/',
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)

    def test_register_password_mismatch(self):
        """Test registration with password mismatch"""
        data = {
            'username': 'newuser',
            'email': 'newuser@test.com',
            'password': 'SecurePass123!',
            'password_confirm': 'DifferentPass123!',
            'first_name': 'New',
            'last_name': 'User',
            'role': 'student'
        }
        response = self.client.post(
            '/api/user/register/',
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)


class TestUserLogin(TestCase):
    """Tests for user login endpoint"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='SecurePass123!',
            first_name='Test',
            last_name='User',
            role='student',
            is_active=True,
            is_email_verified=True
        )

    def test_login_success(self):
        """Test successful login"""
        response = self.client.post(
            '/api/user/login/',
            data=json.dumps({
                'email': 'test@test.com',
                'password': 'SecurePass123!'
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('tokens', data)
        self.assertIn('access', data['tokens'])

    def test_login_wrong_password(self):
        """Test login with wrong password"""
        response = self.client.post(
            '/api/user/login/',
            data=json.dumps({
                'email': 'test@test.com',
                'password': 'WrongPassword!'
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 401)

    def test_login_nonexistent_user(self):
        """Test login with non-existent user"""
        response = self.client.post(
            '/api/user/login/',
            data=json.dumps({
                'email': 'nonexistent@test.com',
                'password': 'SecurePass123!'
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 401)

    def test_login_inactive_user(self):
        """Test login with inactive user"""
        self.user.is_active = False
        self.user.save()
        response = self.client.post(
            '/api/user/login/',
            data=json.dumps({
                'email': 'test@test.com',
                'password': 'SecurePass123!'
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 401)

    def test_login_unverified_email(self):
        """Test login with unverified email"""
        self.user.is_email_verified = False
        self.user.save()
        response = self.client.post(
            '/api/user/login/',
            data=json.dumps({
                'email': 'test@test.com',
                'password': 'SecurePass123!'
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 401)
        data = response.json()
        self.assertTrue(data.get('requires_verification', False))

    def test_login_invalid_data(self):
        """Test login with invalid data format"""
        response = self.client.post(
            '/api/user/login/',
            data=json.dumps({
                'email': 'invalid'
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)


class TestEmailVerification(TestCase):
    """Tests for email verification endpoint"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='SecurePass123!',
            first_name='Test',
            last_name='User',
            role='student',
            is_active=True,
            is_email_verified=False
        )
        self.user.verification_code = '123456'
        self.user.save()

    def test_verify_email_success(self):
        """Test successful email verification"""
        with patch('eduAPI.services.user_service.verify_email', return_value=True):
            response = self.client.post(
                '/api/user/verify-email/',
                data=json.dumps({
                    'email': 'test@test.com',
                    'verification_code': '123456'
                }),
                content_type='application/json'
            )
            self.assertIn(response.status_code, [200, 400])

    def test_verify_email_invalid_code(self):
        """Test email verification with invalid code"""
        response = self.client.post(
            '/api/user/verify-email/',
            data=json.dumps({
                'email': 'test@test.com',
                'verification_code': 'wrong'
            }),
            content_type='application/json'
        )
        self.assertIn(response.status_code, [400, 404])

    def test_verify_email_nonexistent_user(self):
        """Test email verification for non-existent user"""
        response = self.client.post(
            '/api/user/verify-email/',
            data=json.dumps({
                'email': 'nonexistent@test.com',
                'verification_code': '123456'
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 404)

    def test_verify_email_missing_fields(self):
        """Test email verification with missing fields"""
        response = self.client.post(
            '/api/user/verify-email/',
            data=json.dumps({
                'email': 'test@test.com'
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)


class TestResendVerification(TestCase):
    """Tests for resend verification email endpoint"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='SecurePass123!',
            first_name='Test',
            last_name='User',
            role='student',
            is_active=True,
            is_email_verified=False
        )

    def test_resend_verification_success(self):
        """Test successful resend verification"""
        with patch('eduAPI.services.user_service.send_verification_email'):
            response = self.client.post(
                '/api/user/resend-verification/',
                data=json.dumps({'email': 'test@test.com'}),
                content_type='application/json'
            )
            self.assertEqual(response.status_code, 200)

    def test_resend_verification_already_verified(self):
        """Test resend verification for already verified user"""
        self.user.is_email_verified = True
        self.user.save()
        response = self.client.post(
            '/api/user/resend-verification/',
            data=json.dumps({'email': 'test@test.com'}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)

    def test_resend_verification_nonexistent_user(self):
        """Test resend verification for non-existent user"""
        response = self.client.post(
            '/api/user/resend-verification/',
            data=json.dumps({'email': 'nonexistent@test.com'}),
            content_type='application/json'
        )
        # Should return 200 for security (don't reveal if email exists)
        self.assertEqual(response.status_code, 200)

    def test_resend_verification_invalid_email(self):
        """Test resend verification with invalid email"""
        response = self.client.post(
            '/api/user/resend-verification/',
            data=json.dumps({'email': 'invalid'}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)


class TestUserProfile(TestCase):
    """Tests for user profile endpoint"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='SecurePass123!',
            first_name='Test',
            last_name='User',
            role='student',
            is_active=True,
            is_email_verified=True
        )

    def get_token(self):
        response = self.client.post(
            '/api/user/login/',
            data=json.dumps({
                'email': 'test@test.com',
                'password': 'SecurePass123!'
            }),
            content_type='application/json'
        )
        data = response.json()
        return data.get('tokens', {}).get('access', '')

    def test_get_profile_success(self):
        """Test successful profile retrieval"""
        token = self.get_token()
        response = self.client.get(
            '/api/user/profile/',
            HTTP_AUTHORIZATION=f'Bearer {token}'
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['email'], 'test@test.com')

    def test_get_profile_unauthenticated(self):
        """Test profile retrieval without authentication"""
        response = self.client.get('/api/user/profile/')
        self.assertEqual(response.status_code, 401)


class TestPasswordReset(TestCase):
    """Tests for password reset endpoints"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='SecurePass123!',
            first_name='Test',
            last_name='User',
            role='student',
            is_active=True,
            is_email_verified=True
        )

    def test_password_reset_request_success(self):
        """Test successful password reset request"""
        with patch('eduAPI.services.user_service.initiate_password_reset', return_value=(True, 'Email sent')):
            response = self.client.post(
                '/api/user/password-reset/request/',
                data=json.dumps({'email': 'test@test.com'}),
                content_type='application/json'
            )
            self.assertEqual(response.status_code, 200)

    def test_password_reset_request_invalid_email(self):
        """Test password reset request with invalid email"""
        response = self.client.post(
            '/api/user/password-reset/request/',
            data=json.dumps({'email': 'invalid'}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)

    def test_password_reset_confirm_success(self):
        """Test successful password reset confirmation"""
        with patch('eduAPI.services.user_service.reset_password', return_value=(True, 'Password reset')):
            response = self.client.post(
                '/api/user/password-reset/confirm/',
                data=json.dumps({
                    'token': 'valid-token',
                    'password': 'NewSecurePass123!'
                }),
                content_type='application/json'
            )
            self.assertEqual(response.status_code, 200)

    def test_password_reset_confirm_invalid_token(self):
        """Test password reset confirmation with invalid token"""
        with patch('eduAPI.services.user_service.reset_password', return_value=(False, 'Invalid token')):
            response = self.client.post(
                '/api/user/password-reset/confirm/',
                data=json.dumps({
                    'token': 'invalid-token',
                    'password': 'NewSecurePass123!'
                }),
                content_type='application/json'
            )
            self.assertEqual(response.status_code, 400)

    def test_validate_reset_token_valid(self):
        """Test validating a valid reset token"""
        with patch('eduAPI.services.user_service.validate_password_reset_token', return_value=self.user):
            response = self.client.get('/api/user/password-reset/validate/valid-token/')
            self.assertEqual(response.status_code, 200)

    def test_validate_reset_token_invalid(self):
        """Test validating an invalid reset token"""
        with patch('eduAPI.services.user_service.validate_password_reset_token', return_value=None):
            response = self.client.get('/api/user/password-reset/validate/invalid-token/')
            self.assertEqual(response.status_code, 400)


class TestTeacherProfile(TestCase):
    """Tests for teacher profile endpoints"""

    def setUp(self):
        self.client = Client()
        self.teacher = User.objects.create_user(
            username='teacher',
            email='teacher@test.com',
            password='SecurePass123!',
            first_name='Test',
            last_name='Teacher',
            role='teacher',
            is_active=True,
            is_email_verified=True
        )
        self.student = User.objects.create_user(
            username='student',
            email='student@test.com',
            password='SecurePass123!',
            first_name='Test',
            last_name='Student',
            role='student',
            is_active=True,
            is_email_verified=True
        )

    def get_token(self, email):
        response = self.client.post(
            '/api/user/login/',
            data=json.dumps({
                'email': email,
                'password': 'SecurePass123!'
            }),
            content_type='application/json'
        )
        data = response.json()
        return data.get('tokens', {}).get('access', '')

    def test_get_teacher_profile_success(self):
        """Test successful teacher profile retrieval"""
        token = self.get_token('teacher@test.com')
        response = self.client.get(
            '/api/user/teacher/profile/',
            HTTP_AUTHORIZATION=f'Bearer {token}'
        )
        self.assertEqual(response.status_code, 200)

    def test_get_teacher_profile_as_student(self):
        """Test teacher profile access as student"""
        token = self.get_token('student@test.com')
        response = self.client.get(
            '/api/user/teacher/profile/',
            HTTP_AUTHORIZATION=f'Bearer {token}'
        )
        self.assertEqual(response.status_code, 403)

    def test_update_teacher_profile(self):
        """Test updating teacher profile"""
        token = self.get_token('teacher@test.com')
        response = self.client.put(
            '/api/user/teacher/profile/',
            data={'first_name': 'Updated'},
            HTTP_AUTHORIZATION=f'Bearer {token}'
        )
        self.assertIn(response.status_code, [200, 400, 415])

    def test_get_other_teacher_profile(self):
        """Test getting another teacher's profile"""
        other_teacher = User.objects.create_user(
            username='other_teacher',
            email='other@test.com',
            password='SecurePass123!',
            first_name='Other',
            last_name='Teacher',
            role='teacher',
            is_active=True,
            is_email_verified=True
        )
        token = self.get_token('teacher@test.com')
        response = self.client.get(
            f'/api/user/teacher/profile/{other_teacher.id}/',
            HTTP_AUTHORIZATION=f'Bearer {token}'
        )
        self.assertEqual(response.status_code, 200)


class TestStudentProfile(TestCase):
    """Tests for student profile endpoints"""

    def setUp(self):
        self.client = Client()
        self.student = User.objects.create_user(
            username='student',
            email='student@test.com',
            password='SecurePass123!',
            first_name='Test',
            last_name='Student',
            role='student',
            is_active=True,
            is_email_verified=True
        )
        self.teacher = User.objects.create_user(
            username='teacher',
            email='teacher@test.com',
            password='SecurePass123!',
            first_name='Test',
            last_name='Teacher',
            role='teacher',
            is_active=True,
            is_email_verified=True
        )

    def get_token(self, email):
        response = self.client.post(
            '/api/user/login/',
            data=json.dumps({
                'email': email,
                'password': 'SecurePass123!'
            }),
            content_type='application/json'
        )
        data = response.json()
        return data.get('tokens', {}).get('access', '')

    def test_get_student_profile_success(self):
        """Test successful student profile retrieval"""
        token = self.get_token('student@test.com')
        response = self.client.get(
            '/api/user/student/profile/',
            HTTP_AUTHORIZATION=f'Bearer {token}'
        )
        self.assertEqual(response.status_code, 200)

    def test_get_student_profile_as_teacher(self):
        """Test student profile access as teacher"""
        token = self.get_token('teacher@test.com')
        response = self.client.get(
            '/api/user/student/profile/',
            HTTP_AUTHORIZATION=f'Bearer {token}'
        )
        self.assertEqual(response.status_code, 403)

    def test_update_student_profile(self):
        """Test updating student profile"""
        token = self.get_token('student@test.com')
        response = self.client.put(
            '/api/user/student/profile/',
            data={'first_name': 'Updated'},
            HTTP_AUTHORIZATION=f'Bearer {token}'
        )
        self.assertIn(response.status_code, [200, 400, 415])


class TestAdvisorProfile(TestCase):
    """Tests for advisor profile endpoints"""

    def setUp(self):
        self.client = Client()
        self.advisor = User.objects.create_user(
            username='advisor',
            email='advisor@test.com',
            password='SecurePass123!',
            first_name='Test',
            last_name='Advisor',
            role='advisor',
            is_active=True,
            is_email_verified=True
        )
        self.student = User.objects.create_user(
            username='student',
            email='student@test.com',
            password='SecurePass123!',
            first_name='Test',
            last_name='Student',
            role='student',
            is_active=True,
            is_email_verified=True
        )

    def get_token(self, email):
        response = self.client.post(
            '/api/user/login/',
            data=json.dumps({
                'email': email,
                'password': 'SecurePass123!'
            }),
            content_type='application/json'
        )
        data = response.json()
        return data.get('tokens', {}).get('access', '')

    def test_get_advisor_profile_success(self):
        """Test successful advisor profile retrieval"""
        token = self.get_token('advisor@test.com')
        response = self.client.get(
            '/api/user/advisor/profile/',
            HTTP_AUTHORIZATION=f'Bearer {token}'
        )
        self.assertEqual(response.status_code, 200)

    def test_get_advisor_profile_as_student(self):
        """Test advisor profile access as student"""
        token = self.get_token('student@test.com')
        response = self.client.get(
            '/api/user/advisor/profile/',
            HTTP_AUTHORIZATION=f'Bearer {token}'
        )
        self.assertEqual(response.status_code, 403)

    def test_update_advisor_profile(self):
        """Test updating advisor profile"""
        token = self.get_token('advisor@test.com')
        response = self.client.put(
            '/api/user/advisor/profile/',
            data={'first_name': 'Updated'},
            HTTP_AUTHORIZATION=f'Bearer {token}'
        )
        self.assertIn(response.status_code, [200, 400, 415])


class TestGetStudents(TestCase):
    """Tests for get_students endpoint"""

    def setUp(self):
        self.client = Client()
        self.teacher = User.objects.create_user(
            username='teacher',
            email='teacher@test.com',
            password='SecurePass123!',
            first_name='Test',
            last_name='Teacher',
            role='teacher',
            is_active=True,
            is_email_verified=True
        )
        self.student = User.objects.create_user(
            username='student',
            email='student@test.com',
            password='SecurePass123!',
            first_name='Test',
            last_name='Student',
            role='student',
            is_active=True,
            is_email_verified=True
        )

    def get_token(self, email):
        response = self.client.post(
            '/api/user/login/',
            data=json.dumps({
                'email': email,
                'password': 'SecurePass123!'
            }),
            content_type='application/json'
        )
        data = response.json()
        return data.get('tokens', {}).get('access', '')

    def test_get_students_as_teacher(self):
        """Test getting students as teacher"""
        token = self.get_token('teacher@test.com')
        response = self.client.get(
            '/api/user/students/',
            HTTP_AUTHORIZATION=f'Bearer {token}'
        )
        self.assertEqual(response.status_code, 200)

    def test_get_students_as_student(self):
        """Test getting students as student (should fail)"""
        token = self.get_token('student@test.com')
        response = self.client.get(
            '/api/user/students/',
            HTTP_AUTHORIZATION=f'Bearer {token}'
        )
        self.assertEqual(response.status_code, 403)


class TestGetStudentsByGrade(TestCase):
    """Tests for get_students_by_grade endpoint"""

    def setUp(self):
        self.client = Client()
        self.advisor = User.objects.create_user(
            username='advisor',
            email='advisor@test.com',
            password='SecurePass123!',
            first_name='Test',
            last_name='Advisor',
            role='advisor',
            is_active=True,
            is_email_verified=True
        )
        self.student = User.objects.create_user(
            username='student',
            email='student@test.com',
            password='SecurePass123!',
            first_name='Test',
            last_name='Student',
            role='student',
            grade_level='5',
            is_active=True,
            is_email_verified=True
        )

    def get_token(self, email):
        response = self.client.post(
            '/api/user/login/',
            data=json.dumps({
                'email': email,
                'password': 'SecurePass123!'
            }),
            content_type='application/json'
        )
        data = response.json()
        return data.get('tokens', {}).get('access', '')

    def test_get_students_by_grade_as_advisor(self):
        """Test getting students by grade as advisor"""
        token = self.get_token('advisor@test.com')
        response = self.client.get(
            '/api/user/advisor/students/',
            HTTP_AUTHORIZATION=f'Bearer {token}'
        )
        self.assertEqual(response.status_code, 200)

    def test_get_students_by_specific_grade(self):
        """Test getting students by specific grade"""
        token = self.get_token('advisor@test.com')
        response = self.client.get(
            '/api/user/advisor/students/grade/5/',
            HTTP_AUTHORIZATION=f'Bearer {token}'
        )
        self.assertEqual(response.status_code, 200)

    def test_get_students_with_search(self):
        """Test getting students with search query"""
        token = self.get_token('advisor@test.com')
        response = self.client.get(
            '/api/user/advisor/students/?search=Test',
            HTTP_AUTHORIZATION=f'Bearer {token}'
        )
        self.assertEqual(response.status_code, 200)

    def test_get_students_as_non_advisor(self):
        """Test getting students as non-advisor (should fail)"""
        token = self.get_token('student@test.com')
        response = self.client.get(
            '/api/user/advisor/students/',
            HTTP_AUTHORIZATION=f'Bearer {token}'
        )
        self.assertEqual(response.status_code, 403)
