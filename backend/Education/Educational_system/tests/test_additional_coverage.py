# Additional tests for user_views.py and student_views.py to increase coverage
import pytest
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from unittest.mock import patch, MagicMock

User = get_user_model()


class TestUserViewsAdditional(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.teacher = User.objects.create_user(
            username='teacher_add1', email='teacher_add@test.com', password='testpass123',
            first_name='Test', last_name='Teacher', role='teacher', is_email_verified=True
        )
        self.student = User.objects.create_user(
            username='student_add1', email='student_add@test.com', password='testpass123',
            first_name='Test', last_name='Student', role='student', is_email_verified=True, grade_level='10'
        )
        self.advisor = User.objects.create_user(
            username='advisor_add1', email='advisor_add@test.com', password='testpass123',
            first_name='Test', last_name='Advisor', role='advisor', is_email_verified=True
        )
    
    def test_teacher_profile_update(self):
        self.client.force_authenticate(user=self.teacher)
        response = self.client.put('/api/user/teacher/profile/', {'first_name': 'Updated'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_student_profile_update(self):
        self.client.force_authenticate(user=self.student)
        response = self.client.put('/api/user/student/profile/', {'first_name': 'Updated'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_advisor_profile_update(self):
        self.client.force_authenticate(user=self.advisor)
        response = self.client.put('/api/user/advisor/profile/', {'first_name': 'Updated'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_get_students_by_grade_specific(self):
        self.client.force_authenticate(user=self.advisor)
        response = self.client.get('/api/user/advisor/students/grade/10/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_get_student_performance(self):
        self.client.force_authenticate(user=self.advisor)
        response = self.client.get(f'/api/user/advisor/students/{self.student.id}/performance/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_get_student_performance_not_advisor(self):
        self.client.force_authenticate(user=self.teacher)
        response = self.client.get(f'/api/user/advisor/students/{self.student.id}/performance/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_get_student_quiz_answers(self):
        self.client.force_authenticate(user=self.teacher)
        response = self.client.get(f'/api/user/students/{self.student.id}/quiz-answers/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_get_student_quiz_answers_not_teacher(self):
        self.client.force_authenticate(user=self.student)
        response = self.client.get(f'/api/user/students/{self.student.id}/quiz-answers/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class TestStudentViewsAdditional(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.teacher = User.objects.create_user(
            username='teacher_stv1', email='teacher_stv@test.com', password='testpass123',
            first_name='Test', last_name='Teacher', role='teacher', is_email_verified=True
        )
        self.student = User.objects.create_user(
            username='student_stv1', email='student_stv@test.com', password='testpass123',
            first_name='Test', last_name='Student', role='student', is_email_verified=True
        )
    
    def test_get_lesson_detail_success(self):
        from eduAPI.models.lessons_model import Lesson
        lesson = Lesson.objects.create(name='Test Lesson', subject='Math', level='10', teacher=self.teacher)
        self.client.force_authenticate(user=self.student)
        response = self.client.get(f'/api/student/lessons/{lesson.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_get_lesson_contents_success(self):
        from eduAPI.models.lessons_model import Lesson
        lesson = Lesson.objects.create(name='Test Lesson', subject='Math', level='10', teacher=self.teacher)
        self.client.force_authenticate(user=self.student)
        response = self.client.get(f'/api/student/lessons/{lesson.id}/contents/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_get_lesson_contents_not_found(self):
        self.client.force_authenticate(user=self.student)
        response = self.client.get('/api/student/lessons/99999/contents/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_submit_quiz_answer_not_found(self):
        self.client.force_authenticate(user=self.student)
        response = self.client.post('/api/student/quiz-attempts/99999/submit-answer/', {'question_id': 1, 'answer_id': 1})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_complete_quiz_attempt_not_found(self):
        self.client.force_authenticate(user=self.student)
        response = self.client.post('/api/student/quiz-attempts/99999/complete/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_submit_quiz_answer_success(self):
        from eduAPI.models.lessons_model import Lesson, Quiz, Question, Answer, QuizAttempt
        lesson = Lesson.objects.create(name='Test Lesson', subject='Math', level='10', teacher=self.teacher)
        quiz = Quiz.objects.create(lesson=lesson, title='Test Quiz', passing_score=70)
        question = Question.objects.create(quiz=quiz, question_text='What is 2+2?', points=10)
        answer = Answer.objects.create(question=question, answer_text='4', is_correct=True)
        attempt = QuizAttempt.objects.create(student=self.student, quiz=quiz, score=0, passed=False)
        self.client.force_authenticate(user=self.student)
        response = self.client.post(f'/api/student/quiz-attempts/{attempt.id}/submit-answer/', {'question_id': question.id, 'answer_id': answer.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_complete_quiz_attempt_success(self):
        from eduAPI.models.lessons_model import Lesson, Quiz, QuizAttempt, StudentEnrollment
        lesson = Lesson.objects.create(name='Test Lesson', subject='Math', level='10', teacher=self.teacher)
        StudentEnrollment.objects.create(student=self.student, lesson=lesson, progress=0)
        quiz = Quiz.objects.create(lesson=lesson, title='Test Quiz', passing_score=70)
        attempt = QuizAttempt.objects.create(student=self.student, quiz=quiz, score=0, passed=False)
        self.client.force_authenticate(user=self.student)
        response = self.client.post(f'/api/student/quiz-attempts/{attempt.id}/complete/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class TestUserServiceAdditional(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='test_svc1', email='test_svc@test.com', password='testpass123',
            first_name='Test', last_name='User', role='student', is_email_verified=False
        )
    
    @patch('eduAPI.services.user_service.send_mail')
    def test_send_verification_email(self, mock_send_mail):
        from eduAPI.services.user_service import send_verification_email
        mock_send_mail.return_value = 1
        send_verification_email(self.user)
        self.assertIsNotNone(self.user.verification_code)
        mock_send_mail.assert_called_once()
    
    def test_verify_email_success(self):
        from eduAPI.services.user_service import verify_email
        self.user.verification_code = '123456'
        self.user.save()
        result = verify_email(self.user, '123456')
        self.assertTrue(result)
        self.user.refresh_from_db()
        self.assertTrue(self.user.is_email_verified)
    
    def test_verify_email_wrong_code(self):
        from eduAPI.services.user_service import verify_email
        self.user.verification_code = '123456'
        self.user.save()
        result = verify_email(self.user, '654321')
        self.assertFalse(result)
    
    def test_get_tokens_for_user(self):
        from eduAPI.services.user_service import get_tokens_for_user
        tokens = get_tokens_for_user(self.user)
        self.assertIn('access', tokens)
        self.assertIn('refresh', tokens)
    
    def test_update_user_profile(self):
        from eduAPI.services.user_service import update_user_profile
        updated = update_user_profile(self.user, {'first_name': 'Updated'})
        self.assertEqual(updated.first_name, 'Updated')
    
    @patch('eduAPI.services.user_service.send_mail')
    def test_initiate_password_reset(self, mock_send_mail):
        from eduAPI.services.user_service import initiate_password_reset
        mock_send_mail.return_value = 1
        success, message = initiate_password_reset(self.user.email)
        self.assertTrue(success)
    
    def test_initiate_password_reset_nonexistent(self):
        from eduAPI.services.user_service import initiate_password_reset
        success, message = initiate_password_reset('nonexistent@test.com')
        self.assertTrue(success)  # Returns success to prevent email enumeration
    
    def test_validate_password_reset_token_invalid(self):
        from eduAPI.services.user_service import validate_password_reset_token
        result = validate_password_reset_token('invalid_token')
        self.assertIsNone(result)
    
    def test_validate_password_reset_token_valid(self):
        from eduAPI.services.user_service import validate_password_reset_token
        from django.utils import timezone
        from datetime import timedelta
        self.user.password_reset_token = 'valid_token'
        self.user.password_reset_expires = timezone.now() + timedelta(hours=24)
        self.user.save()
        result = validate_password_reset_token('valid_token')
        self.assertEqual(result, self.user)
    
    def test_reset_password_success(self):
        from eduAPI.services.user_service import reset_password
        from django.utils import timezone
        from datetime import timedelta
        self.user.password_reset_token = 'valid_token'
        self.user.password_reset_expires = timezone.now() + timedelta(hours=24)
        self.user.save()
        success, message = reset_password('valid_token', 'newpassword123')
        self.assertTrue(success)
    
    def test_reset_password_invalid_token(self):
        from eduAPI.services.user_service import reset_password
        success, message = reset_password('invalid_token', 'newpassword123')
        self.assertFalse(success)
