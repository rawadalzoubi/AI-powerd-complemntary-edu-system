"""
Comprehensive Services Tests
Tests for service layer to increase coverage
"""
import json
from django.test import TestCase
from django.contrib.auth import get_user_model
from unittest.mock import patch, MagicMock
from eduAPI.models.lessons_model import Lesson, LessonContent, Quiz, Question, Answer, StudentEnrollment
from eduAPI.services.lessons_service import LessonService, LessonContentService, QuizService, QuestionService, AnswerService

User = get_user_model()


class TestLessonService(TestCase):
    """Tests for LessonService"""

    def setUp(self):
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
        self.lesson = Lesson.objects.create(
            name='Test Lesson',
            description='Test Description',
            subject='Math',
            level='5',
            teacher=self.teacher
        )

    def test_get_teacher_lessons(self):
        """Test getting lessons for a teacher"""
        lessons = LessonService.get_teacher_lessons(self.teacher.id)
        self.assertEqual(lessons.count(), 1)

    def test_get_lesson_by_id(self):
        """Test getting a lesson by ID"""
        lesson = LessonService.get_lesson_by_id(self.lesson.id, self.teacher.id)
        self.assertIsNotNone(lesson)
        self.assertEqual(lesson.name, 'Test Lesson')

    def test_get_lesson_by_id_not_found(self):
        """Test getting a non-existent lesson"""
        lesson = LessonService.get_lesson_by_id(99999, self.teacher.id)
        self.assertIsNone(lesson)

    def test_create_lesson(self):
        """Test creating a lesson"""
        data = {
            'name': 'New Lesson',
            'description': 'New Description',
            'subject': 'Science',
            'level': '6'
        }
        lesson = LessonService.create_lesson(data, self.teacher.id)
        self.assertIsNotNone(lesson)
        self.assertEqual(lesson.name, 'New Lesson')

    def test_update_lesson(self):
        """Test updating a lesson"""
        data = {
            'name': 'Updated Lesson'
        }
        updated = LessonService.update_lesson(self.lesson.id, data, self.teacher.id)
        self.assertIsNotNone(updated)
        self.assertEqual(updated.name, 'Updated Lesson')

    def test_delete_lesson(self):
        """Test deleting a lesson"""
        result = LessonService.delete_lesson(self.lesson.id, self.teacher.id)
        self.assertTrue(result)
        self.assertFalse(Lesson.objects.filter(id=self.lesson.id).exists())

    def test_delete_lesson_not_found(self):
        """Test deleting a non-existent lesson"""
        result = LessonService.delete_lesson(99999, self.teacher.id)
        self.assertFalse(result)


class TestLessonContentService(TestCase):
    """Tests for LessonContentService"""

    def setUp(self):
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
        self.lesson = Lesson.objects.create(
            name='Test Lesson',
            description='Test Description',
            subject='Math',
            level='5',
            teacher=self.teacher
        )
        self.content = LessonContent.objects.create(
            lesson=self.lesson,
            title='Test Content',
            content_type='text',
            text_content='Test text'
        )

    def test_get_lesson_contents(self):
        """Test getting contents for a lesson"""
        contents = LessonContentService.get_lesson_contents(self.lesson.id)
        self.assertEqual(contents.count(), 1)

    def test_create_content(self):
        """Test creating lesson content"""
        data = {
            'title': 'New Content',
            'content_type': 'text',
            'text_content': 'New text'
        }
        content = LessonContentService.create_content(self.lesson.id, data, None)
        self.assertIsNotNone(content)
        self.assertEqual(content.title, 'New Content')

    def test_delete_content(self):
        """Test deleting lesson content"""
        result = LessonContentService.delete_content(self.content.id, self.teacher.id)
        self.assertTrue(result)


class TestQuizService(TestCase):
    """Tests for QuizService"""

    def setUp(self):
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
        self.lesson = Lesson.objects.create(
            name='Test Lesson',
            description='Test Description',
            subject='Math',
            level='5',
            teacher=self.teacher
        )
        self.quiz = Quiz.objects.create(
            lesson=self.lesson,
            title='Test Quiz',
            description='Test Quiz Description'
        )

    def test_get_lesson_quizzes(self):
        """Test getting quizzes for a lesson"""
        quizzes = QuizService.get_lesson_quizzes(self.lesson.id)
        self.assertEqual(quizzes.count(), 1)

    def test_get_quiz_by_id(self):
        """Test getting a quiz by ID"""
        quiz = QuizService.get_quiz_by_id(self.quiz.id, self.teacher.id)
        self.assertIsNotNone(quiz)
        self.assertEqual(quiz.title, 'Test Quiz')

    def test_get_quiz_by_id_not_found(self):
        """Test getting a non-existent quiz"""
        quiz = QuizService.get_quiz_by_id(99999, self.teacher.id)
        self.assertIsNone(quiz)

    def test_create_quiz(self):
        """Test creating a quiz"""
        data = {
            'title': 'New Quiz',
            'description': 'New Quiz Description'
        }
        quiz = QuizService.create_quiz(self.lesson.id, data)
        self.assertIsNotNone(quiz)
        self.assertEqual(quiz.title, 'New Quiz')

    def test_update_quiz(self):
        """Test updating a quiz"""
        data = {
            'title': 'Updated Quiz'
        }
        updated = QuizService.update_quiz(self.quiz.id, data, self.teacher.id)
        self.assertIsNotNone(updated)
        self.assertEqual(updated.title, 'Updated Quiz')

    def test_delete_quiz(self):
        """Test deleting a quiz"""
        result = QuizService.delete_quiz(self.quiz.id, self.teacher.id)
        self.assertTrue(result)


class TestQuestionService(TestCase):
    """Tests for QuestionService"""

    def setUp(self):
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
        self.lesson = Lesson.objects.create(
            name='Test Lesson',
            description='Test Description',
            subject='Math',
            level='5',
            teacher=self.teacher
        )
        self.quiz = Quiz.objects.create(
            lesson=self.lesson,
            title='Test Quiz',
            description='Test Quiz Description'
        )
        self.question = Question.objects.create(
            quiz=self.quiz,
            question_text='What is 2+2?',
            question_type='multiple_choice'
        )

    def test_get_question_by_id(self):
        """Test getting a question by ID"""
        question = QuestionService.get_question_by_id(self.question.id, self.teacher.id)
        self.assertIsNotNone(question)
        self.assertEqual(question.question_text, 'What is 2+2?')

    def test_get_question_by_id_not_found(self):
        """Test getting a non-existent question"""
        question = QuestionService.get_question_by_id(99999, self.teacher.id)
        self.assertIsNone(question)

    def test_create_question(self):
        """Test creating a question"""
        data = {
            'question_text': 'What is 3+3?',
            'question_type': 'multiple_choice'
        }
        question = QuestionService.create_question(self.quiz.id, data)
        self.assertIsNotNone(question)
        self.assertEqual(question.question_text, 'What is 3+3?')

    def test_update_question(self):
        """Test updating a question"""
        data = {
            'question_text': 'Updated question?'
        }
        updated = QuestionService.update_question(self.question.id, data, self.teacher.id)
        self.assertIsNotNone(updated)
        self.assertEqual(updated.question_text, 'Updated question?')

    def test_delete_question(self):
        """Test deleting a question"""
        result = QuestionService.delete_question(self.question.id, self.teacher.id)
        self.assertTrue(result)


class TestAnswerService(TestCase):
    """Tests for AnswerService"""

    def setUp(self):
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
        self.lesson = Lesson.objects.create(
            name='Test Lesson',
            description='Test Description',
            subject='Math',
            level='5',
            teacher=self.teacher
        )
        self.quiz = Quiz.objects.create(
            lesson=self.lesson,
            title='Test Quiz',
            description='Test Quiz Description'
        )
        self.question = Question.objects.create(
            quiz=self.quiz,
            question_text='What is 2+2?',
            question_type='multiple_choice'
        )
        self.answer = Answer.objects.create(
            question=self.question,
            answer_text='4',
            is_correct=True
        )

    def test_get_answer_by_id(self):
        """Test getting an answer by ID"""
        answer = AnswerService.get_answer_by_id(self.answer.id, self.teacher.id)
        self.assertIsNotNone(answer)
        self.assertEqual(answer.answer_text, '4')

    def test_get_answer_by_id_not_found(self):
        """Test getting a non-existent answer"""
        answer = AnswerService.get_answer_by_id(99999, self.teacher.id)
        self.assertIsNone(answer)

    def test_create_answer(self):
        """Test creating an answer"""
        data = {
            'answer_text': '5',
            'is_correct': False
        }
        answer = AnswerService.create_answer(self.question.id, data)
        self.assertIsNotNone(answer)
        self.assertEqual(answer.answer_text, '5')

    def test_update_answer(self):
        """Test updating an answer"""
        data = {
            'answer_text': 'Updated answer'
        }
        updated = AnswerService.update_answer(self.answer.id, data, self.teacher.id)
        self.assertIsNotNone(updated)
        self.assertEqual(updated.answer_text, 'Updated answer')

    def test_delete_answer(self):
        """Test deleting an answer"""
        result = AnswerService.delete_answer(self.answer.id, self.teacher.id)
        self.assertTrue(result)


class TestUserService(TestCase):
    """Tests for user_service"""

    def setUp(self):
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

    def test_send_verification_email(self):
        """Test sending verification email"""
        from eduAPI.services import user_service
        with patch('eduAPI.services.user_service.send_mail') as mock_send:
            mock_send.return_value = 1
            user_service.send_verification_email(self.user)
            # Should have set verification code
            self.user.refresh_from_db()
            self.assertIsNotNone(self.user.verification_code)

    def test_verify_email_success(self):
        """Test successful email verification"""
        from eduAPI.services import user_service
        self.user.verification_code = '123456'
        self.user.save()
        result = user_service.verify_email(self.user, '123456')
        self.assertTrue(result)
        self.user.refresh_from_db()
        self.assertTrue(self.user.is_email_verified)

    def test_verify_email_wrong_code(self):
        """Test email verification with wrong code"""
        from eduAPI.services import user_service
        self.user.verification_code = '123456'
        self.user.save()
        result = user_service.verify_email(self.user, 'wrong')
        self.assertFalse(result)

    def test_initiate_password_reset(self):
        """Test initiating password reset"""
        from eduAPI.services import user_service
        with patch('eduAPI.services.user_service.send_mail') as mock_send:
            mock_send.return_value = 1
            success, message = user_service.initiate_password_reset('test@test.com')
            self.assertTrue(success)

    def test_initiate_password_reset_nonexistent_user(self):
        """Test initiating password reset for non-existent user"""
        from eduAPI.services import user_service
        success, message = user_service.initiate_password_reset('nonexistent@test.com')
        # Should still return success for security
        self.assertTrue(success)

    def test_validate_password_reset_token_invalid(self):
        """Test validating invalid password reset token"""
        from eduAPI.services import user_service
        result = user_service.validate_password_reset_token('invalid-token')
        self.assertIsNone(result)
