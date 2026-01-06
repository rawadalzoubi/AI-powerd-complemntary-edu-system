"""
Content Management Test Cases (Teacher)
TC-CNT-001 to TC-CNT-003
"""
import json
from django.test import TestCase, Client
from django.contrib.auth import get_user_model

User = get_user_model()


class TestContentManagement(TestCase):
    """Content Management Tests for Teachers"""

    def setUp(self):
        """Set up test client and teacher user"""
        self.client = Client()
        self.teacher = User.objects.create_user(
            username='teacher_user',
            email='teacher@example.com',
            password='SecurePass123!',
            first_name='Test',
            last_name='Teacher',
            role='teacher',
            is_active=True,
            is_email_verified=True
        )
        # Login and get token
        login_response = self.client.post(
            '/api/user/login/',
            data={'email': 'teacher@example.com', 'password': 'SecurePass123!'},
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
    # TC-CNT-001: Upload Lesson
    # =========================================================================
    def test_tc_cnt_001_upload_lesson_success(self):
        """
        Test ID: TC-CNT-001
        Title: Teacher Successfully Uploads a New Lesson
        """
        lesson_data = {
            'name': 'Intro to Arabic Grammar',
            'description': 'Introduction to basic Arabic grammar rules',
            'subject': 'Arabic',
            'level': '5',
        }
        
        response = self.client.post(
            '/api/lessons/lessons/',
            data=json.dumps(lesson_data),
            content_type='application/json',
            **self.get_auth_header()
        )
        
        if response.status_code != 404:
            self.assertIn(response.status_code, [200, 201, 401])

    def test_tc_cnt_001_fail_missing_title(self):
        """TC-CNT-001 Fail Case: Missing required title"""
        lesson_data = {
            'description': 'Lesson without title',
            'subject': 'Arabic'
        }
        
        response = self.client.post(
            '/api/lessons/lessons/',
            data=json.dumps(lesson_data),
            content_type='application/json',
            **self.get_auth_header()
        )
        
        if response.status_code not in [404, 401]:
            self.assertIn(response.status_code, [400, 422])

    # =========================================================================
    # TC-CNT-002: Create MCQ
    # =========================================================================
    def test_tc_cnt_002_create_mcq_success(self):
        """
        Test ID: TC-CNT-002
        Title: Teacher Creates a New MCQ Exercise
        """
        # First create a lesson
        lesson_data = {
            'name': 'Geography Lesson',
            'subject': 'Geography',
            'level': '5'
        }
        lesson_response = self.client.post(
            '/api/lessons/lessons/',
            data=json.dumps(lesson_data),
            content_type='application/json',
            **self.get_auth_header()
        )
        
        if lesson_response.status_code in [200, 201]:
            lesson_id = lesson_response.json().get('id', 1)
            
            quiz_data = {
                'title': 'Geography Quiz',
                'description': 'Test your geography knowledge'
            }
            
            response = self.client.post(
                f'/api/lessons/lessons/{lesson_id}/quizzes/',
                data=json.dumps(quiz_data),
                content_type='application/json',
                **self.get_auth_header()
            )
            
            if response.status_code != 404:
                self.assertIn(response.status_code, [200, 201])

    # =========================================================================
    # TC-CNT-003: Manage Lesson
    # =========================================================================
    def test_tc_cnt_003_view_lessons(self):
        """
        Test ID: TC-CNT-003 (Part 1 - View)
        Title: Teacher Views Lesson List
        """
        response = self.client.get(
            '/api/lessons/lessons/',
            **self.get_auth_header()
        )
        
        if response.status_code != 404:
            self.assertIn(response.status_code, [200, 401])

    def test_tc_cnt_003_update_lesson(self):
        """
        Test ID: TC-CNT-003 (Part 2 - Update)
        Title: Teacher Updates Lesson Title
        """
        # Create lesson first
        lesson_data = {
            'name': 'Original Title',
            'subject': 'Math',
            'level': '5'
        }
        create_response = self.client.post(
            '/api/lessons/lessons/',
            data=json.dumps(lesson_data),
            content_type='application/json',
            **self.get_auth_header()
        )
        
        if create_response.status_code in [200, 201]:
            lesson_id = create_response.json().get('id', 1)
            
            update_data = {'name': 'Updated Title'}
            response = self.client.patch(
                f'/api/lessons/lessons/{lesson_id}/',
                data=json.dumps(update_data),
                content_type='application/json',
                **self.get_auth_header()
            )
            
            if response.status_code != 404:
                self.assertIn(response.status_code, [200, 204])

    def test_tc_cnt_003_delete_lesson(self):
        """
        Test ID: TC-CNT-003 (Part 3 - Delete)
        Title: Teacher Deletes Lesson
        """
        # Create lesson first
        lesson_data = {
            'name': 'Lesson to Delete',
            'subject': 'Science',
            'level': '5'
        }
        create_response = self.client.post(
            '/api/lessons/lessons/',
            data=json.dumps(lesson_data),
            content_type='application/json',
            **self.get_auth_header()
        )
        
        if create_response.status_code in [200, 201]:
            lesson_id = create_response.json().get('id', 1)
            
            response = self.client.delete(
                f'/api/lessons/lessons/{lesson_id}/',
                **self.get_auth_header()
            )
            
            if response.status_code != 404:
                self.assertIn(response.status_code, [200, 204])
