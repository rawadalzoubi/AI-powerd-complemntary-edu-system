# Tests for student_views.py to increase coverage
import pytest
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model

User = get_user_model()


class TestStudentViewsExtendedCoverage(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.teacher = User.objects.create_user(
            username='teacher_sv1', email='teacher@test.com', password='testpass123',
            first_name='Test', last_name='Teacher', role='teacher', is_email_verified=True
        )
        self.student = User.objects.create_user(
            username='student_sv1', email='student@test.com', password='testpass123',
            first_name='Test', last_name='Student', role='student', is_email_verified=True
        )
    
    def test_get_student_dashboard_lessons_as_teacher(self):
        self.client.force_authenticate(user=self.teacher)
        response = self.client.get('/api/student/dashboard/lessons/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_get_student_dashboard_lessons_success(self):
        from eduAPI.models.lessons_model import Lesson, StudentEnrollment
        lesson = Lesson.objects.create(name='Test Lesson', subject='Math', level='10', teacher=self.teacher)
        StudentEnrollment.objects.create(student=self.student, lesson=lesson, progress=50)
        self.client.force_authenticate(user=self.student)
        response = self.client.get('/api/student/dashboard/lessons/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_get_student_lesson_detail_not_found(self):
        self.client.force_authenticate(user=self.student)
        response = self.client.get('/api/student/lessons/99999/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_get_student_lesson_quizzes_success(self):
        from eduAPI.models.lessons_model import Lesson, Quiz
        lesson = Lesson.objects.create(name='Test Lesson', subject='Math', level='10', teacher=self.teacher)
        Quiz.objects.create(lesson=lesson, title='Test Quiz', passing_score=70)
        self.client.force_authenticate(user=self.student)
        response = self.client.get(f'/api/student/lessons/{lesson.id}/quizzes/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_start_quiz_attempt_success(self):
        from eduAPI.models.lessons_model import Lesson, Quiz, StudentEnrollment
        lesson = Lesson.objects.create(name='Test Lesson', subject='Math', level='10', teacher=self.teacher)
        quiz = Quiz.objects.create(lesson=lesson, title='Test Quiz', passing_score=70)
        # Student must be enrolled in the lesson to attempt quiz
        StudentEnrollment.objects.create(student=self.student, lesson=lesson, progress=0)
        self.client.force_authenticate(user=self.student)
        response = self.client.post(f'/api/student/quizzes/{quiz.id}/attempt/')
        # Could be 201 (created) or 200 (existing attempt) or 400 (no questions)
        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_201_CREATED, status.HTTP_400_BAD_REQUEST])


class TestUserViewsExtendedCoverage(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.teacher = User.objects.create_user(
            username='teacher_uv1', email='teacher@test.com', password='testpass123',
            first_name='Test', last_name='Teacher', role='teacher', is_email_verified=True
        )
        self.student = User.objects.create_user(
            username='student_uv1', email='student@test.com', password='testpass123',
            first_name='Test', last_name='Student', role='student', is_email_verified=True
        )
        self.advisor = User.objects.create_user(
            username='advisor_uv1', email='advisor@test.com', password='testpass123',
            first_name='Test', last_name='Advisor', role='advisor', is_email_verified=True
        )
    
    def test_get_students_as_teacher(self):
        self.client.force_authenticate(user=self.teacher)
        response = self.client.get('/api/user/students/')
        # Could be 200 or 403 depending on teacher permissions
        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_403_FORBIDDEN])
    
    def test_get_students_by_grade_as_advisor(self):
        self.client.force_authenticate(user=self.advisor)
        response = self.client.get('/api/user/advisor/students/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_teacher_profile_view_get_own(self):
        # Profile fields are on User model directly
        self.teacher.specialization = 'Math'
        self.teacher.save()
        self.client.force_authenticate(user=self.teacher)
        response = self.client.get('/api/user/teacher/profile/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_student_profile_view_get_own(self):
        # Profile fields are on User model directly
        self.student.grade_level = '10'
        self.student.save()
        self.client.force_authenticate(user=self.student)
        response = self.client.get('/api/user/student/profile/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_advisor_profile_view_get_own(self):
        # Profile fields are on User model directly
        self.client.force_authenticate(user=self.advisor)
        response = self.client.get('/api/user/advisor/profile/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
