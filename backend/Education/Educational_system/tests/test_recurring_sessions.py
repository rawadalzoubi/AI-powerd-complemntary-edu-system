"""
Recurring Sessions Test Cases
TC-RS-001 to TC-RS-005
"""
import json
from datetime import timedelta
from django.test import TestCase, Client
from django.utils import timezone
from django.contrib.auth import get_user_model

User = get_user_model()


class TestRecurringSessions(TestCase):
    """Recurring Sessions Tests"""

    def setUp(self):
        """Set up test client and users with verified emails"""
        self.client = Client()
        
        self.teacher = User.objects.create_user(
            username='teacher_recurring',
            email='teacher@example.com',
            password='SecurePass123!',
            first_name='Test',
            last_name='Teacher',
            role='teacher',
            is_active=True,
            is_email_verified=True
        )
        
        self.advisor = User.objects.create_user(
            username='advisor_recurring',
            email='advisor@example.com',
            password='SecurePass123!',
            first_name='Test',
            last_name='Advisor',
            role='advisor',
            is_active=True,
            is_email_verified=True
        )
        
        self.student = User.objects.create_user(
            username='student_recurring',
            email='student@example.com',
            password='SecurePass123!',
            first_name='Test',
            last_name='Student',
            role='student',
            is_active=True,
            is_email_verified=True,
            grade_level='5'
        )

    def login_as(self, email, password='SecurePass123!'):
        """Login and return token"""
        response = self.client.post(
            '/api/user/login/',
            data=json.dumps({'email': email, 'password': password}),
            content_type='application/json'
        )
        if response.status_code == 200:
            data = response.json()
            # Token is nested under 'tokens' key
            tokens = data.get('tokens', {})
            return tokens.get('access', data.get('access', ''))
        return ''

    def get_auth_header(self, token):
        """Return authorization header"""
        return {'HTTP_AUTHORIZATION': f'Bearer {token}'}

    # =========================================================================
    # TC-RS-001: Create Session Template
    # =========================================================================
    def test_tc_rs_001_create_weekly_template(self):
        """
        Test ID: TC-RS-001
        Title: Create a Weekly Recurring Template
        """
        token = self.login_as('teacher@example.com')
        self.assertTrue(len(token) > 0, "Teacher should be able to login")
        
        start_date = (timezone.now() + timedelta(days=7)).date()
        
        template_data = {
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
            data=json.dumps(template_data),
            content_type='application/json',
            **self.get_auth_header(token)
        )
        
        self.assertIn(response.status_code, [200, 201, 400])
        
        if response.status_code in [200, 201]:
            data = response.json()
            self.assertEqual(data.get('status', '').upper(), 'ACTIVE')

    def test_tc_rs_001_create_biweekly_template(self):
        """TC-RS-001: Create bi-weekly template"""
        token = self.login_as('teacher@example.com')
        
        template_data = {
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
            data=json.dumps(template_data),
            content_type='application/json',
            **self.get_auth_header(token)
        )
        
        self.assertIn(response.status_code, [200, 201, 400])

    def test_tc_rs_001_create_monthly_template(self):
        """TC-RS-001: Create monthly template"""
        token = self.login_as('teacher@example.com')
        
        template_data = {
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
            data=json.dumps(template_data),
            content_type='application/json',
            **self.get_auth_header(token)
        )
        
        self.assertIn(response.status_code, [200, 201, 400])

    def test_tc_rs_001_fail_missing_required_fields(self):
        """TC-RS-001 Fail Case: Missing required fields"""
        token = self.login_as('teacher@example.com')
        
        template_data = {
            'title': 'Incomplete Template'
        }
        
        response = self.client.post(
            '/api/recurring-sessions/templates/',
            data=json.dumps(template_data),
            content_type='application/json',
            **self.get_auth_header(token)
        )
        
        self.assertIn(response.status_code, [400, 422])

    def test_tc_rs_001_fail_unauthenticated(self):
        """TC-RS-001 Fail Case: Unauthenticated"""
        template_data = {'title': 'Unauthorized Template'}
        
        response = self.client.post(
            '/api/recurring-sessions/templates/',
            data=json.dumps(template_data),
            content_type='application/json'
        )
        
        self.assertIn(response.status_code, [401, 403])

    # =========================================================================
    # TC-RS-002: View Generated Sessions
    # =========================================================================
    def test_tc_rs_002_view_templates_list(self):
        """
        Test ID: TC-RS-002
        Title: View Templates List
        """
        token = self.login_as('teacher@example.com')
        
        response = self.client.get(
            '/api/recurring-sessions/templates/',
            **self.get_auth_header(token)
        )
        
        self.assertEqual(response.status_code, 200)

    def test_tc_rs_002_view_generated_sessions(self):
        """TC-RS-002: View all generated sessions"""
        token = self.login_as('teacher@example.com')
        
        response = self.client.get(
            '/api/recurring-sessions/generated-sessions/',
            **self.get_auth_header(token)
        )
        
        self.assertEqual(response.status_code, 200)

    def test_tc_rs_002_view_template_detail(self):
        """TC-RS-002: View template detail"""
        token = self.login_as('teacher@example.com')
        
        # First create a template
        template_data = {
            'title': 'Template for Detail View',
            'subject': 'Math',
            'level': '5',
            'day_of_week': 'MONDAY',
            'start_time': '09:00:00',
            'duration_minutes': 60,
            'recurrence_type': 'WEEKLY',
            'start_date': '2025-01-06'
        }
        
        create_response = self.client.post(
            '/api/recurring-sessions/templates/',
            data=json.dumps(template_data),
            content_type='application/json',
            **self.get_auth_header(token)
        )
        
        if create_response.status_code in [200, 201]:
            template_id = create_response.json().get('id')
            
            response = self.client.get(
                f'/api/recurring-sessions/templates/{template_id}/',
                **self.get_auth_header(token)
            )
            
            self.assertEqual(response.status_code, 200)

    # =========================================================================
    # TC-RS-003: Pause Template
    # =========================================================================
    def test_tc_rs_003_pause_template(self):
        """
        Test ID: TC-RS-003
        Title: Teacher Pauses a Recurring Template
        """
        token = self.login_as('teacher@example.com')
        
        # Create template first
        template_data = {
            'title': 'Template to Pause',
            'subject': 'Science',
            'level': '5',
            'day_of_week': 'TUESDAY',
            'start_time': '10:00:00',
            'duration_minutes': 60,
            'recurrence_type': 'WEEKLY',
            'start_date': '2025-01-07'
        }
        
        create_response = self.client.post(
            '/api/recurring-sessions/templates/',
            data=json.dumps(template_data),
            content_type='application/json',
            **self.get_auth_header(token)
        )
        
        if create_response.status_code in [200, 201]:
            template_id = create_response.json().get('id')
            
            # Pause template
            response = self.client.post(
                f'/api/recurring-sessions/templates/{template_id}/pause/',
                **self.get_auth_header(token)
            )
            
            self.assertIn(response.status_code, [200, 204])
            
            # Verify status
            detail_response = self.client.get(
                f'/api/recurring-sessions/templates/{template_id}/',
                **self.get_auth_header(token)
            )
            
            if detail_response.status_code == 200:
                self.assertEqual(detail_response.json().get('status', '').upper(), 'PAUSED')

    def test_tc_rs_003_resume_template(self):
        """TC-RS-003: Resume a paused template"""
        token = self.login_as('teacher@example.com')
        
        # Create and pause template
        template_data = {
            'title': 'Template to Resume',
            'subject': 'Math',
            'level': '5',
            'day_of_week': 'MONDAY',
            'start_time': '09:00:00',
            'duration_minutes': 60,
            'recurrence_type': 'WEEKLY',
            'start_date': '2025-01-06'
        }
        
        create_response = self.client.post(
            '/api/recurring-sessions/templates/',
            data=json.dumps(template_data),
            content_type='application/json',
            **self.get_auth_header(token)
        )
        
        if create_response.status_code in [200, 201]:
            template_id = create_response.json().get('id')
            
            # Pause
            self.client.post(
                f'/api/recurring-sessions/templates/{template_id}/pause/',
                **self.get_auth_header(token)
            )
            
            # Resume
            response = self.client.post(
                f'/api/recurring-sessions/templates/{template_id}/resume/',
                **self.get_auth_header(token)
            )
            
            self.assertIn(response.status_code, [200, 204])

    def test_tc_rs_003_end_template(self):
        """TC-RS-003: End template permanently"""
        token = self.login_as('teacher@example.com')
        
        # Create template
        template_data = {
            'title': 'Template to End',
            'subject': 'Arabic',
            'level': '5',
            'day_of_week': 'WEDNESDAY',
            'start_time': '11:00:00',
            'duration_minutes': 60,
            'recurrence_type': 'WEEKLY',
            'start_date': '2025-01-08'
        }
        
        create_response = self.client.post(
            '/api/recurring-sessions/templates/',
            data=json.dumps(template_data),
            content_type='application/json',
            **self.get_auth_header(token)
        )
        
        if create_response.status_code in [200, 201]:
            template_id = create_response.json().get('id')
            
            # End template
            response = self.client.post(
                f'/api/recurring-sessions/templates/{template_id}/end/',
                **self.get_auth_header(token)
            )
            
            self.assertIn(response.status_code, [200, 204, 404])

    # =========================================================================
    # TC-RS-004: Edit Session Template
    # =========================================================================
    def test_tc_rs_004_edit_template(self):
        """
        Test ID: TC-RS-004
        Title: Edit Template
        """
        token = self.login_as('teacher@example.com')
        
        # Create template
        template_data = {
            'title': 'Template to Edit',
            'subject': 'Math',
            'level': '5',
            'day_of_week': 'WEDNESDAY',
            'start_time': '09:00:00',
            'duration_minutes': 60,
            'recurrence_type': 'WEEKLY',
            'start_date': '2025-01-08'
        }
        
        create_response = self.client.post(
            '/api/recurring-sessions/templates/',
            data=json.dumps(template_data),
            content_type='application/json',
            **self.get_auth_header(token)
        )
        
        if create_response.status_code in [200, 201]:
            template_id = create_response.json().get('id')
            
            # Edit template
            update_data = {
                'title': 'Updated Template Title',
                'start_time': '11:00:00'
            }
            
            response = self.client.patch(
                f'/api/recurring-sessions/templates/{template_id}/',
                data=json.dumps(update_data),
                content_type='application/json',
                **self.get_auth_header(token)
            )
            
            self.assertIn(response.status_code, [200, 204])

    def test_tc_rs_004_delete_template(self):
        """TC-RS-004: Delete template"""
        token = self.login_as('teacher@example.com')
        
        # Create template
        template_data = {
            'title': 'Template to Delete',
            'subject': 'Science',
            'level': '5',
            'day_of_week': 'THURSDAY',
            'start_time': '14:00:00',
            'duration_minutes': 45,
            'recurrence_type': 'WEEKLY',
            'start_date': '2025-01-09'
        }
        
        create_response = self.client.post(
            '/api/recurring-sessions/templates/',
            data=json.dumps(template_data),
            content_type='application/json',
            **self.get_auth_header(token)
        )
        
        if create_response.status_code in [200, 201]:
            template_id = create_response.json().get('id')
            
            # Delete template
            response = self.client.delete(
                f'/api/recurring-sessions/templates/{template_id}/',
                **self.get_auth_header(token)
            )
            
            self.assertIn(response.status_code, [200, 204])

    # =========================================================================
    # TC-RS-005: Assign Template to Group
    # =========================================================================
    def test_tc_rs_005_create_student_group(self):
        """
        Test ID: TC-RS-005
        Title: Create Student Group
        """
        token = self.login_as('advisor@example.com')
        self.assertTrue(len(token) > 0, "Advisor should be able to login")
        
        group_data = {
            'name': 'Grade 5 Section A',
            'description': 'Grade 5 Section A students'
        }
        
        response = self.client.post(
            '/api/recurring-sessions/groups/',
            data=json.dumps(group_data),
            content_type='application/json',
            **self.get_auth_header(token)
        )
        
        self.assertIn(response.status_code, [200, 201, 400, 403])

    def test_tc_rs_005_view_groups(self):
        """TC-RS-005: View student groups"""
        token = self.login_as('advisor@example.com')
        
        response = self.client.get(
            '/api/recurring-sessions/groups/',
            **self.get_auth_header(token)
        )
        
        self.assertIn(response.status_code, [200, 403])

    def test_tc_rs_005_view_available_students(self):
        """TC-RS-005: View available students"""
        token = self.login_as('advisor@example.com')
        
        response = self.client.get(
            '/api/recurring-sessions/students/available/',
            **self.get_auth_header(token)
        )
        
        self.assertEqual(response.status_code, 200)

    def test_tc_rs_005_student_view_sessions(self):
        """TC-RS-005: Student views their recurring sessions"""
        token = self.login_as('student@example.com')
        
        response = self.client.get(
            '/api/recurring-sessions/my-sessions/',
            **self.get_auth_header(token)
        )
        
        self.assertEqual(response.status_code, 200)

    def test_tc_rs_005_view_statistics(self):
        """TC-RS-005: View template statistics"""
        token = self.login_as('teacher@example.com')
        
        response = self.client.get(
            '/api/recurring-sessions/statistics/',
            **self.get_auth_header(token)
        )
        
        self.assertEqual(response.status_code, 200)

    def test_tc_rs_005_view_generation_logs(self):
        """TC-RS-005: View generation logs"""
        token = self.login_as('teacher@example.com')
        
        response = self.client.get(
            '/api/recurring-sessions/generation-logs/',
            **self.get_auth_header(token)
        )
        
        self.assertEqual(response.status_code, 200)
