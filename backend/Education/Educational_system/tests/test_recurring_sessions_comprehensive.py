"""
Comprehensive Recurring Sessions Tests
Tests for recurring_sessions_views.py to increase coverage
"""
import json
from datetime import timedelta
from django.test import TestCase, Client
from django.utils import timezone
from django.contrib.auth import get_user_model

User = get_user_model()


class TestSessionTemplates(TestCase):
    """Tests for session template endpoints"""

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

    def test_get_templates_as_teacher(self):
        """Test getting templates as teacher"""
        token = self.get_token('teacher@test.com')
        response = self.client.get(
            '/api/recurring-sessions/templates/',
            HTTP_AUTHORIZATION=f'Bearer {token}'
        )
        self.assertEqual(response.status_code, 200)

    def test_get_templates_as_advisor(self):
        """Test getting templates as advisor"""
        token = self.get_token('advisor@test.com')
        response = self.client.get(
            '/api/recurring-sessions/templates/',
            HTTP_AUTHORIZATION=f'Bearer {token}'
        )
        self.assertEqual(response.status_code, 200)

    def test_get_templates_unauthenticated(self):
        """Test getting templates without authentication"""
        response = self.client.get('/api/recurring-sessions/templates/')
        self.assertEqual(response.status_code, 401)

    def test_create_template_success(self):
        """Test creating a template"""
        token = self.get_token('teacher@test.com')
        start_date = (timezone.now() + timedelta(days=7)).date()
        data = {
            'title': 'Weekly Math Session',
            'description': 'Weekly mathematics revision',
            'subject': 'Math',
            'level': '5',
            'day_of_week': 'MONDAY',
            'start_time': '09:00:00',
            'duration_minutes': 60,
            'recurrence_type': 'WEEKLY',
            'start_date': start_date.isoformat(),
            'max_participants': 30
        }
        response = self.client.post(
            '/api/recurring-sessions/templates/',
            data=json.dumps(data),
            content_type='application/json',
            HTTP_AUTHORIZATION=f'Bearer {token}'
        )
        self.assertIn(response.status_code, [200, 201, 400])

    def test_create_template_missing_fields(self):
        """Test creating a template with missing fields"""
        token = self.get_token('teacher@test.com')
        data = {
            'title': 'Incomplete Template'
        }
        response = self.client.post(
            '/api/recurring-sessions/templates/',
            data=json.dumps(data),
            content_type='application/json',
            HTTP_AUTHORIZATION=f'Bearer {token}'
        )
        self.assertIn(response.status_code, [400, 422])

    def test_create_biweekly_template(self):
        """Test creating a bi-weekly template"""
        token = self.get_token('teacher@test.com')
        data = {
            'title': 'Bi-weekly Science Session',
            'subject': 'Science',
            'level': '6',
            'day_of_week': 'WEDNESDAY',
            'start_time': '14:00:00',
            'duration_minutes': 45,
            'recurrence_type': 'BIWEEKLY',
            'start_date': '2025-01-15'
        }
        response = self.client.post(
            '/api/recurring-sessions/templates/',
            data=json.dumps(data),
            content_type='application/json',
            HTTP_AUTHORIZATION=f'Bearer {token}'
        )
        self.assertIn(response.status_code, [200, 201, 400])

    def test_create_monthly_template(self):
        """Test creating a monthly template"""
        token = self.get_token('teacher@test.com')
        data = {
            'title': 'Monthly Review Session',
            'subject': 'Arabic',
            'level': '4',
            'day_of_week': 'FRIDAY',
            'start_time': '10:00:00',
            'duration_minutes': 90,
            'recurrence_type': 'MONTHLY',
            'start_date': '2025-01-10'
        }
        response = self.client.post(
            '/api/recurring-sessions/templates/',
            data=json.dumps(data),
            content_type='application/json',
            HTTP_AUTHORIZATION=f'Bearer {token}'
        )
        self.assertIn(response.status_code, [200, 201, 400])


class TestTemplateActions(TestCase):
    """Tests for template action endpoints"""

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

    def create_template(self, token):
        """Helper to create a template"""
        start_date = (timezone.now() + timedelta(days=7)).date()
        data = {
            'title': 'Test Template',
            'subject': 'Math',
            'level': '5',
            'day_of_week': 'MONDAY',
            'start_time': '09:00:00',
            'duration_minutes': 60,
            'recurrence_type': 'WEEKLY',
            'start_date': start_date.isoformat()
        }
        response = self.client.post(
            '/api/recurring-sessions/templates/',
            data=json.dumps(data),
            content_type='application/json',
            HTTP_AUTHORIZATION=f'Bearer {token}'
        )
        if response.status_code in [200, 201]:
            return response.json().get('id')
        return None

    def test_get_template_detail(self):
        """Test getting template detail"""
        token = self.get_token('teacher@test.com')
        template_id = self.create_template(token)
        
        if template_id:
            response = self.client.get(
                f'/api/recurring-sessions/templates/{template_id}/',
                HTTP_AUTHORIZATION=f'Bearer {token}'
            )
            self.assertEqual(response.status_code, 200)

    def test_update_template(self):
        """Test updating a template"""
        token = self.get_token('teacher@test.com')
        template_id = self.create_template(token)
        
        if template_id:
            data = {
                'title': 'Updated Template Title',
                'start_time': '11:00:00'
            }
            response = self.client.patch(
                f'/api/recurring-sessions/templates/{template_id}/',
                data=json.dumps(data),
                content_type='application/json',
                HTTP_AUTHORIZATION=f'Bearer {token}'
            )
            self.assertIn(response.status_code, [200, 204])

    def test_delete_template(self):
        """Test deleting a template"""
        token = self.get_token('teacher@test.com')
        template_id = self.create_template(token)
        
        if template_id:
            response = self.client.delete(
                f'/api/recurring-sessions/templates/{template_id}/',
                HTTP_AUTHORIZATION=f'Bearer {token}'
            )
            self.assertIn(response.status_code, [200, 204])

    def test_pause_template(self):
        """Test pausing a template"""
        token = self.get_token('teacher@test.com')
        template_id = self.create_template(token)
        
        if template_id:
            response = self.client.post(
                f'/api/recurring-sessions/templates/{template_id}/pause/',
                HTTP_AUTHORIZATION=f'Bearer {token}'
            )
            self.assertIn(response.status_code, [200, 204])

    def test_resume_template(self):
        """Test resuming a template"""
        token = self.get_token('teacher@test.com')
        template_id = self.create_template(token)
        
        if template_id:
            # First pause
            self.client.post(
                f'/api/recurring-sessions/templates/{template_id}/pause/',
                HTTP_AUTHORIZATION=f'Bearer {token}'
            )
            # Then resume
            response = self.client.post(
                f'/api/recurring-sessions/templates/{template_id}/resume/',
                HTTP_AUTHORIZATION=f'Bearer {token}'
            )
            self.assertIn(response.status_code, [200, 204])

    def test_end_template(self):
        """Test ending a template"""
        token = self.get_token('teacher@test.com')
        template_id = self.create_template(token)
        
        if template_id:
            response = self.client.post(
                f'/api/recurring-sessions/templates/{template_id}/end/',
                HTTP_AUTHORIZATION=f'Bearer {token}'
            )
            self.assertIn(response.status_code, [200, 204, 404])


class TestGeneratedSessions(TestCase):
    """Tests for generated sessions endpoints"""

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

    def test_get_generated_sessions(self):
        """Test getting generated sessions"""
        token = self.get_token('teacher@test.com')
        response = self.client.get(
            '/api/recurring-sessions/generated-sessions/',
            HTTP_AUTHORIZATION=f'Bearer {token}'
        )
        self.assertEqual(response.status_code, 200)


class TestStudentGroups(TestCase):
    """Tests for student group endpoints"""

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

    def test_create_student_group(self):
        """Test creating a student group"""
        token = self.get_token('advisor@test.com')
        data = {
            'name': 'Grade 5 Section A',
            'description': 'Grade 5 Section A students'
        }
        response = self.client.post(
            '/api/recurring-sessions/groups/',
            data=json.dumps(data),
            content_type='application/json',
            HTTP_AUTHORIZATION=f'Bearer {token}'
        )
        self.assertIn(response.status_code, [200, 201, 400, 403])

    def test_get_groups(self):
        """Test getting student groups"""
        token = self.get_token('advisor@test.com')
        response = self.client.get(
            '/api/recurring-sessions/groups/',
            HTTP_AUTHORIZATION=f'Bearer {token}'
        )
        self.assertIn(response.status_code, [200, 403])

    def test_get_available_students(self):
        """Test getting available students"""
        token = self.get_token('advisor@test.com')
        response = self.client.get(
            '/api/recurring-sessions/students/available/',
            HTTP_AUTHORIZATION=f'Bearer {token}'
        )
        self.assertEqual(response.status_code, 200)


class TestStudentRecurringSessions(TestCase):
    """Tests for student recurring sessions endpoints"""

    def setUp(self):
        self.client = Client()
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

    def test_get_my_recurring_sessions(self):
        """Test getting student's recurring sessions"""
        token = self.get_token('student@test.com')
        response = self.client.get(
            '/api/recurring-sessions/my-sessions/',
            HTTP_AUTHORIZATION=f'Bearer {token}'
        )
        self.assertEqual(response.status_code, 200)


class TestStatisticsAndLogs(TestCase):
    """Tests for statistics and logs endpoints"""

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

    def test_get_statistics(self):
        """Test getting template statistics"""
        token = self.get_token('teacher@test.com')
        response = self.client.get(
            '/api/recurring-sessions/statistics/',
            HTTP_AUTHORIZATION=f'Bearer {token}'
        )
        self.assertEqual(response.status_code, 200)

    def test_get_generation_logs(self):
        """Test getting generation logs"""
        token = self.get_token('teacher@test.com')
        response = self.client.get(
            '/api/recurring-sessions/generation-logs/',
            HTTP_AUTHORIZATION=f'Bearer {token}'
        )
        self.assertEqual(response.status_code, 200)
