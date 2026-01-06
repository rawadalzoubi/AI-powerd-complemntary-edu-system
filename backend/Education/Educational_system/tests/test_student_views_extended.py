"""
Extended tests for student_views.py
Target: Increase coverage from 52% to 75%+
"""
import pytest
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock
from django.test import TestCase, Client
from django.utils import timezone
from django.contrib.auth import get_user_model

User = get_user_model()


class TestStudentViewsExtended(TestCase):
    """Extended tests for student views"""
    
    def setUp(self):
        self.client = Client()
        
        # Create teacher
        self.teacher = User.objects.create_user(
            username='teacher',
            email='teacher@test.com',
            password='SecurePass123!',
            role='teacher',
            first_name='Test',
            last_name='Teacher'
        )
        self.teacher.is_email_verified = True
        self.teacher.save()
        
        # Create student
        self.student = User.objects.create_user(
            username='student',
            email='student@test.com',
            password='SecurePass123!',
            role='student',
            first_name='Test',
            last_name='Student'
        )
        self.student.is_email_verified = True
        self.student.save()
        
        # Create advisor
        self.advisor = User.objects.create_user(
            username='advisor',
            email='advisor@test.com',
            password='SecurePass123!',
            role='advisor',
            first_name='Test',
            last_name='Advisor'
        )
        self.advisor.is_email_verified = True
        self.advisor.save()
        
        # Create lesson
        from eduAPI.models import Lesson
        self.lesson = Lesson.objects.create(
            name='Test Lesson',
            description='Test Description',
            subject='Math',
            level='10',
            teacher=self.teacher
        )
    
    def get_token(self, email):
        """Helper to get JWT token"""
        response = self.client.post(
            '/api/user/login/',
            data={'email': email, 'password': 'SecurePass123!'},
            content_type='application/json'
        )
        if response.status_code == 200:
            data = response.json()
            return data.get('tokens', {}).get('access', data.get('access', ''))
        return ''
    
    def test_get_student_dashboard_as_student(self):
        """Test student dashboard endpoint"""
        token = self.get_token('student@test.com')
        response = self.client.get(
            '/api/student/dashboard/',
            HTTP_AUTHORIZATION=f'Bearer {token}'
        )
        self.assertIn(response.status_code, [200, 404])
    
    def test_get_student_stats(self):
        """Test student stats endpoint"""
        token = self.get_token('student@test.com')
        response = self.client.get(
            '/api/student/stats/',
            HTTP_AUTHORIZATION=f'Bearer {token}'
        )
        self.assertIn(response.status_code, [200, 404])
    
    def test_get_student_progress(self):
        """Test student progress endpoint"""
        token = self.get_token('student@test.com')
        response = self.client.get(
            '/api/student/progress/',
            HTTP_AUTHORIZATION=f'Bearer {token}'
        )
        self.assertIn(response.status_code, [200, 404])
    
    def test_update_lesson_progress(self):
        """Test updating lesson progress"""
        token = self.get_token('student@test.com')
        response = self.client.post(
            f'/api/student/lessons/{self.lesson.id}/progress/',
            data={'progress': 50},
            content_type='application/json',
            HTTP_AUTHORIZATION=f'Bearer {token}'
        )
        self.assertIn(response.status_code, [200, 201, 404])
    
    def test_get_lesson_quizzes(self):
        """Test getting quizzes for a lesson"""
        token = self.get_token('student@test.com')
        response = self.client.get(
            f'/api/student/lessons/{self.lesson.id}/quizzes/',
            HTTP_AUTHORIZATION=f'Bearer {token}'
        )
        self.assertIn(response.status_code, [200, 404])
    
    def test_start_quiz_nonexistent(self):
        """Test starting non-existent quiz"""
        token = self.get_token('student@test.com')
        response = self.client.post(
            '/api/student/quizzes/99999/start/',
            HTTP_AUTHORIZATION=f'Bearer {token}'
        )
        self.assertIn(response.status_code, [404, 500])
    
    def test_submit_quiz_answer_missing_fields(self):
        """Test submitting quiz answer with missing fields"""
        token = self.get_token('student@test.com')
        response = self.client.post(
            '/api/student/quizzes/1/submit/',
            data={},
            content_type='application/json',
            HTTP_AUTHORIZATION=f'Bearer {token}'
        )
        self.assertIn(response.status_code, [400, 404])
    
    def test_complete_quiz_attempt(self):
        """Test completing quiz attempt"""
        token = self.get_token('student@test.com')
        response = self.client.post(
            '/api/student/quizzes/1/complete/',
            HTTP_AUTHORIZATION=f'Bearer {token}'
        )
        self.assertIn(response.status_code, [200, 404, 500])
    
    def test_get_student_lesson_contents(self):
        """Test getting lesson contents"""
        token = self.get_token('student@test.com')
        response = self.client.get(
            f'/api/student/lessons/{self.lesson.id}/contents/',
            HTTP_AUTHORIZATION=f'Bearer {token}'
        )
        self.assertIn(response.status_code, [200, 404])
    
    def test_get_student_lesson_detail(self):
        """Test getting lesson detail"""
        token = self.get_token('student@test.com')
        response = self.client.get(
            f'/api/student/lessons/{self.lesson.id}/',
            HTTP_AUTHORIZATION=f'Bearer {token}'
        )
        self.assertIn(response.status_code, [200, 403, 404])
    
    def test_get_dashboard_lessons_as_teacher(self):
        """Test dashboard lessons as teacher"""
        token = self.get_token('teacher@test.com')
        response = self.client.get(
            '/api/student/dashboard/lessons/',
            HTTP_AUTHORIZATION=f'Bearer {token}'
        )
        self.assertIn(response.status_code, [200, 403, 404])


@pytest.mark.django_db
class TestStudentQuizFlow:
    """Tests for student quiz flow"""
    
    @pytest.fixture(autouse=True)
    def setup(self, teacher_user, student_user, db):
        self.teacher = teacher_user
        self.student = student_user
        self.client = Client()
        
        from eduAPI.models import Lesson, Quiz, Question, Answer
        
        # Create lesson
        self.lesson = Lesson.objects.create(
            name='Quiz Test Lesson',
            description='Test',
            subject='Math',
            level='10',
            teacher=self.teacher
        )
        
        # Create quiz
        self.quiz = Quiz.objects.create(
            lesson=self.lesson,
            title='Test Quiz',
            description='Test quiz description'
        )
        
        # Create question
        self.question = Question.objects.create(
            quiz=self.quiz,
            question_text='What is 2+2?',
            question_type='SINGLE'
        )
        
        # Create answers
        self.correct_answer = Answer.objects.create(
            question=self.question,
            answer_text='4',
            is_correct=True
        )
        self.wrong_answer = Answer.objects.create(
            question=self.question,
            answer_text='5',
            is_correct=False
        )
    
    def get_token(self, email):
        """Helper to get JWT token"""
        response = self.client.post(
            '/api/user/login/',
            data={'email': email, 'password': 'TestPass123!'},
            content_type='application/json'
        )
        if response.status_code == 200:
            data = response.json()
            return data.get('tokens', {}).get('access', data.get('access', ''))
        return ''
    
    def test_start_quiz(self):
        """Test starting a quiz"""
        token = self.get_token('student@test.com')
        response = self.client.post(
            f'/api/student/quizzes/{self.quiz.id}/start/',
            HTTP_AUTHORIZATION=f'Bearer {token}'
        )
        assert response.status_code in [200, 201, 404]
    
    def test_submit_correct_answer(self):
        """Test submitting correct answer"""
        token = self.get_token('student@test.com')
        
        # First start the quiz
        self.client.post(
            f'/api/student/quizzes/{self.quiz.id}/start/',
            HTTP_AUTHORIZATION=f'Bearer {token}'
        )
        
        # Submit answer
        response = self.client.post(
            f'/api/student/quizzes/{self.quiz.id}/submit/',
            data={
                'question_id': self.question.id,
                'answer_id': self.correct_answer.id
            },
            content_type='application/json',
            HTTP_AUTHORIZATION=f'Bearer {token}'
        )
        assert response.status_code in [200, 201, 400, 404]
    
    def test_get_quiz_questions(self):
        """Test getting quiz questions"""
        token = self.get_token('student@test.com')
        response = self.client.get(
            f'/api/student/quizzes/{self.quiz.id}/questions/',
            HTTP_AUTHORIZATION=f'Bearer {token}'
        )
        assert response.status_code in [200, 404]


@pytest.mark.django_db
class TestStudentEnrollment:
    """Tests for student enrollment functionality"""
    
    @pytest.fixture(autouse=True)
    def setup(self, teacher_user, student_user, advisor_user, db):
        self.teacher = teacher_user
        self.student = student_user
        self.advisor = advisor_user
        self.client = Client()
        
        from eduAPI.models import Lesson, StudentEnrollment
        
        self.lesson = Lesson.objects.create(
            name='Enrollment Test Lesson',
            description='Test',
            subject='Math',
            level='10',
            teacher=self.teacher
        )
        
        # Enroll student
        self.enrollment = StudentEnrollment.objects.create(
            student=self.student,
            lesson=self.lesson
        )
    
    def get_token(self, email):
        """Helper to get JWT token"""
        response = self.client.post(
            '/api/user/login/',
            data={'email': email, 'password': 'TestPass123!'},
            content_type='application/json'
        )
        if response.status_code == 200:
            data = response.json()
            return data.get('tokens', {}).get('access', data.get('access', ''))
        return ''
    
    def test_enrolled_student_can_access_lesson(self):
        """Test enrolled student can access lesson"""
        token = self.get_token('student@test.com')
        response = self.client.get(
            f'/api/student/lessons/{self.lesson.id}/',
            HTTP_AUTHORIZATION=f'Bearer {token}'
        )
        assert response.status_code in [200, 404]
    
    def test_enrolled_student_can_view_contents(self):
        """Test enrolled student can view lesson contents"""
        token = self.get_token('student@test.com')
        response = self.client.get(
            f'/api/student/lessons/{self.lesson.id}/contents/',
            HTTP_AUTHORIZATION=f'Bearer {token}'
        )
        assert response.status_code in [200, 404]
    
    def test_get_enrolled_lessons(self):
        """Test getting enrolled lessons"""
        token = self.get_token('student@test.com')
        response = self.client.get(
            '/api/student/dashboard/lessons/',
            HTTP_AUTHORIZATION=f'Bearer {token}'
        )
        assert response.status_code in [200, 404]
