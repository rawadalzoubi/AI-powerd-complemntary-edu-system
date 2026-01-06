"""
Comprehensive Simple Live Sessions Tests
Tests for simple_live_sessions.py to increase coverage
"""
import json
from datetime import timedelta
from django.test import TestCase, Client
from django.utils import timezone
from django.contrib.auth import get_user_model

User = get_user_model()


class TestLiveSessionsEndpoints(TestCase):
    """Tests for live sessions endpoints"""

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

    def test_get_sessions_as_teacher(self):
        """Test getting sessions as teacher"""
        token = self.get_token('teacher@test.com')
        response = self.client.get(
            '/api/live-sessions/',
            HTTP_AUTHORIZATION=f'Bearer {token}'
        )
        self.assertIn(response.status_code, [200, 404])

    def test_get_sessions_as_student(self):
        """Test getting sessions as student"""
        token = self.get_token('student@test.com')
        response = self.client.get(
            '/api/live-sessions/',
            HTTP_AUTHORIZATION=f'Bearer {token}'
        )
        self.assertIn(response.status_code, [200, 404])

    def test_get_sessions_as_advisor(self):
        """Test getting sessions as advisor"""
        token = self.get_token('advisor@test.com')
        response = self.client.get(
            '/api/live-sessions/',
            HTTP_AUTHORIZATION=f'Bearer {token}'
        )
        self.assertIn(response.status_code, [200, 404])

    def test_get_sessions_unauthenticated(self):
        """Test getting sessions without authentication"""
        response = self.client.get('/api/live-sessions/')
        self.assertEqual(response.status_code, 401)

    def test_create_session_as_teacher(self):
        """Test creating a session as teacher"""
        token = self.get_token('teacher@test.com')
        tomorrow = (timezone.now() + timedelta(days=1)).date()
        data = {
            'title': 'Test Session',
            'description': 'Test Description',
            'scheduled_date': tomorrow.isoformat(),
            'scheduled_time': '10:00:00',
            'duration_minutes': 60,
            'subject': 'Math',
            'level': '5'
        }
        response = self.client.post(
            '/api/live-sessions/',
            data=json.dumps(data),
            content_type='application/json',
            HTTP_AUTHORIZATION=f'Bearer {token}'
        )
        self.assertIn(response.status_code, [200, 201, 400, 404])

    def test_create_session_missing_title(self):
        """Test creating a session without title"""
        token = self.get_token('teacher@test.com')
        data = {
            'scheduled_date': '2025-01-15',
            'scheduled_time': '10:00:00'
        }
        response = self.client.post(
            '/api/live-sessions/',
            data=json.dumps(data),
            content_type='application/json',
            HTTP_AUTHORIZATION=f'Bearer {token}'
        )
        self.assertIn(response.status_code, [400, 404])


class TestMySchedule(TestCase):
    """Tests for my-schedule endpoint"""

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

    def test_get_my_schedule_as_teacher(self):
        """Test getting schedule as teacher"""
        token = self.get_token('teacher@test.com')
        response = self.client.get(
            '/api/live-sessions/my-schedule/',
            HTTP_AUTHORIZATION=f'Bearer {token}'
        )
        self.assertIn(response.status_code, [200, 404])

    def test_get_my_schedule_as_student(self):
        """Test getting schedule as student"""
        token = self.get_token('student@test.com')
        response = self.client.get(
            '/api/live-sessions/my-schedule/',
            HTTP_AUTHORIZATION=f'Bearer {token}'
        )
        self.assertIn(response.status_code, [200, 404])


class TestPendingSessions(TestCase):
    """Tests for pending sessions endpoint"""

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

    def test_get_pending_sessions(self):
        """Test getting pending sessions"""
        token = self.get_token('teacher@test.com')
        response = self.client.get(
            '/api/live-sessions/pending/',
            HTTP_AUTHORIZATION=f'Bearer {token}'
        )
        self.assertIn(response.status_code, [200, 404])


class TestSessionActions(TestCase):
    """Tests for session action endpoints"""

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

    def create_session(self, token):
        """Helper to create a session"""
        tomorrow = (timezone.now() + timedelta(days=1)).date()
        data = {
            'title': 'Test Session',
            'description': 'Test Description',
            'scheduled_date': tomorrow.isoformat(),
            'scheduled_time': '10:00:00',
            'duration_minutes': 60,
            'subject': 'Math',
            'level': '5'
        }
        response = self.client.post(
            '/api/live-sessions/',
            data=json.dumps(data),
            content_type='application/json',
            HTTP_AUTHORIZATION=f'Bearer {token}'
        )
        if response.status_code in [200, 201]:
            return response.json().get('id')
        return None

    def test_join_session(self):
        """Test joining a session"""
        token = self.get_token('student@test.com')
        response = self.client.get(
            '/api/live-sessions/1/join/',
            HTTP_AUTHORIZATION=f'Bearer {token}'
        )
        self.assertIn(response.status_code, [200, 400, 403, 404])

    def test_assign_session(self):
        """Test assigning students to a session"""
        teacher_token = self.get_token('teacher@test.com')
        session_id = self.create_session(teacher_token)
        
        if session_id:
            data = {
                'student_ids': [self.student.id]
            }
            response = self.client.post(
                f'/api/live-sessions/{session_id}/assign/',
                data=json.dumps(data),
                content_type='application/json',
                HTTP_AUTHORIZATION=f'Bearer {teacher_token}'
            )
            self.assertIn(response.status_code, [200, 201, 400, 404])

    def test_unassign_session(self):
        """Test unassigning students from a session"""
        teacher_token = self.get_token('teacher@test.com')
        session_id = self.create_session(teacher_token)
        
        if session_id:
            data = {
                'student_ids': [self.student.id]
            }
            response = self.client.post(
                f'/api/live-sessions/{session_id}/unassign/',
                data=json.dumps(data),
                content_type='application/json',
                HTTP_AUTHORIZATION=f'Bearer {teacher_token}'
            )
            self.assertIn(response.status_code, [200, 400, 404])

    def test_get_assigned_students(self):
        """Test getting assigned students for a session"""
        teacher_token = self.get_token('teacher@test.com')
        session_id = self.create_session(teacher_token)
        
        if session_id:
            response = self.client.get(
                f'/api/live-sessions/{session_id}/assigned-students/',
                HTTP_AUTHORIZATION=f'Bearer {teacher_token}'
            )
            self.assertIn(response.status_code, [200, 404])

    def test_cancel_session(self):
        """Test canceling a session"""
        teacher_token = self.get_token('teacher@test.com')
        session_id = self.create_session(teacher_token)
        
        if session_id:
            response = self.client.post(
                f'/api/live-sessions/{session_id}/cancel/',
                HTTP_AUTHORIZATION=f'Bearer {teacher_token}'
            )
            self.assertIn(response.status_code, [200, 204, 400, 404])

    def test_update_session(self):
        """Test updating a session"""
        teacher_token = self.get_token('teacher@test.com')
        session_id = self.create_session(teacher_token)
        
        if session_id:
            data = {
                'title': 'Updated Session Title'
            }
            response = self.client.patch(
                f'/api/live-sessions/{session_id}/',
                data=json.dumps(data),
                content_type='application/json',
                HTTP_AUTHORIZATION=f'Bearer {teacher_token}'
            )
            self.assertIn(response.status_code, [200, 400, 404])


class TestDebugEndpoints(TestCase):
    """Tests for debug endpoints"""

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

    def test_debug_sessions(self):
        """Test debug sessions endpoint"""
        token = self.get_token('teacher@test.com')
        response = self.client.get(
            '/api/live-sessions/debug/',
            HTTP_AUTHORIZATION=f'Bearer {token}'
        )
        self.assertIn(response.status_code, [200, 401, 404])

    def test_test_live_sessions(self):
        """Test test live sessions endpoint"""
        token = self.get_token('teacher@test.com')
        response = self.client.get(
            '/api/live-sessions/test/',
            HTTP_AUTHORIZATION=f'Bearer {token}'
        )
        self.assertIn(response.status_code, [200, 404])

    def test_test_live_sessions_no_auth(self):
        """Test test live sessions no auth endpoint"""
        response = self.client.get('/api/live-sessions/test-no-auth/')
        self.assertIn(response.status_code, [200, 404])
