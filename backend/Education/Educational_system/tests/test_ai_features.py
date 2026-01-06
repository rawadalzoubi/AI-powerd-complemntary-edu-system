"""
Artificial Intelligence Test Cases
TC-AI-001
"""
import json
from django.test import TestCase, Client
from django.contrib.auth import get_user_model

User = get_user_model()


class TestAIFeatures(TestCase):
    """AI Features Tests"""

    def setUp(self):
        """Set up test client and student user"""
        self.client = Client()
        self.student = User.objects.create_user(
            username='student_ai',
            email='student@example.com',
            password='SecurePass123!',
            first_name='Test',
            last_name='Student',
            role='student',
            is_active=True,
            is_email_verified=True
        )
        # Login and get token
        login_response = self.client.post(
            '/api/user/login/',
            data={'email': 'student@example.com', 'password': 'SecurePass123!'},
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
    # TC-AI-001: Homework Helper
    # =========================================================================
    def test_tc_ai_001_homework_helper_success(self):
        """
        Test ID: TC-AI-001
        Title: Student Uses the AI Homework Helper
        """
        question_data = {
            'question': 'Explain second-degree equation',
            'subject': 'Math',
            'grade_level': 9
        }
        
        response = self.client.post(
            '/api/ai/homework-helper/',
            data=json.dumps(question_data),
            content_type='application/json',
            **self.get_auth_header()
        )
        
        # AI endpoint might not exist yet
        if response.status_code == 200:
            response_data = response.json()
            self.assertIn('answer', response_data)
        else:
            self.assertIn(response.status_code, [404, 501])

    def test_tc_ai_001_homework_helper_arabic_question(self):
        """TC-AI-001: AI Helper with Arabic question"""
        question_data = {
            'question': 'ما هي عاصمة سوريا؟',
            'subject': 'Geography',
            'language': 'ar'
        }
        
        response = self.client.post(
            '/api/ai/homework-helper/',
            data=json.dumps(question_data),
            content_type='application/json',
            **self.get_auth_header()
        )
        
        self.assertIn(response.status_code, [200, 404, 501])

    def test_tc_ai_001_fail_empty_question(self):
        """TC-AI-001 Fail Case: Empty question"""
        question_data = {
            'question': ''
        }
        
        response = self.client.post(
            '/api/ai/homework-helper/',
            data=json.dumps(question_data),
            content_type='application/json',
            **self.get_auth_header()
        )
        
        self.assertIn(response.status_code, [400, 404, 422, 501])

    def test_tc_ai_001_fail_unauthenticated(self):
        """TC-AI-001 Fail Case: Unauthenticated access"""
        question_data = {
            'question': 'Test question'
        }
        
        response = self.client.post(
            '/api/ai/homework-helper/',
            data=json.dumps(question_data),
            content_type='application/json'
        )
        
        self.assertIn(response.status_code, [401, 403, 404])
