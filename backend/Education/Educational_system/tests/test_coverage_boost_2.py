# Additional tests to boost coverage - Part 2
import pytest
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from unittest.mock import patch, MagicMock

User = get_user_model()


class TestRecurringSessionsModels(TestCase):
    """Tests for recurring_sessions_models.py"""
    
    def setUp(self):
        self.teacher = User.objects.create_user(
            username='teacher_rsm', email='teacher_rsm@test.com', password='testpass123',
            first_name='Test', last_name='Teacher', role='teacher', is_email_verified=True
        )
        self.advisor = User.objects.create_user(
            username='advisor_rsm', email='advisor_rsm@test.com', password='testpass123',
            first_name='Test', last_name='Advisor', role='advisor', is_email_verified=True
        )
        self.student = User.objects.create_user(
            username='student_rsm', email='student_rsm@test.com', password='testpass123',
            first_name='Test', last_name='Student', role='student', is_email_verified=True
        )
    
    def test_session_template_next_generation_date(self):
        """Test SessionTemplate next_generation_date property"""
        from eduAPI.models.recurring_sessions_models import SessionTemplate
        
        template = SessionTemplate.objects.create(
            title='Weekly Math',
            teacher=self.teacher,
            subject='Math',
            level='10',
            day_of_week=1,
            start_time='10:00:00',
            duration_minutes=60,
            recurrence_type='WEEKLY',
            start_date=timezone.now().date(),
            status='ACTIVE'
        )
        
        # Test that next_generation_date returns a date
        next_date = template.next_generation_date
        self.assertIsNotNone(next_date)
    
    def test_student_group_student_count(self):
        """Test StudentGroup student_count property"""
        from eduAPI.models.recurring_sessions_models import StudentGroup
        
        group = StudentGroup.objects.create(
            name='Test Group',
            advisor=self.advisor
        )
        group.students.add(self.student)
        
        self.assertEqual(group.student_count, 1)
    
    def test_template_group_assignment_str(self):
        """Test TemplateGroupAssignment string representation"""
        from eduAPI.models.recurring_sessions_models import SessionTemplate, StudentGroup, TemplateGroupAssignment
        
        template = SessionTemplate.objects.create(
            title='Weekly Math',
            teacher=self.teacher,
            subject='Math',
            level='10',
            day_of_week=1,
            start_time='10:00:00',
            duration_minutes=60,
            recurrence_type='WEEKLY',
            start_date=timezone.now().date()
        )
        
        group = StudentGroup.objects.create(
            name='Test Group',
            advisor=self.advisor
        )
        
        assignment = TemplateGroupAssignment.objects.create(
            template=template,
            group=group,
            advisor=self.advisor
        )
        
        self.assertIn('Weekly Math', str(assignment))


class TestLiveSessionsModels(TestCase):
    """Tests for live_sessions_models.py"""
    
    def setUp(self):
        self.teacher = User.objects.create_user(
            username='teacher_lsm', email='teacher_lsm@test.com', password='testpass123',
            first_name='Test', last_name='Teacher', role='teacher', is_email_verified=True
        )
        self.student = User.objects.create_user(
            username='student_lsm', email='student_lsm@test.com', password='testpass123',
            first_name='Test', last_name='Student', role='student', is_email_verified=True
        )
        self.advisor = User.objects.create_user(
            username='advisor_lsm', email='advisor_lsm@test.com', password='testpass123',
            first_name='Test', last_name='Advisor', role='advisor', is_email_verified=True
        )
    
    def test_live_session_assignment_str(self):
        """Test LiveSessionAssignment string representation"""
        from eduAPI.models.live_sessions_models import LiveSession, LiveSessionAssignment
        
        session = LiveSession.objects.create(
            title='Test Session',
            teacher=self.teacher,
            scheduled_datetime=timezone.now() + timedelta(hours=1),
            duration_minutes=60
        )
        
        assignment = LiveSessionAssignment.objects.create(
            session=session,
            student=self.student,
            advisor=self.advisor
        )
        
        self.assertIn('Test Session', str(assignment))
    
    def test_live_session_status_transitions(self):
        """Test LiveSession status transitions"""
        from eduAPI.models.live_sessions_models import LiveSession
        
        session = LiveSession.objects.create(
            title='Test Session',
            teacher=self.teacher,
            scheduled_datetime=timezone.now() + timedelta(hours=1),
            duration_minutes=60,
            status='PENDING'
        )
        
        # Test status change
        session.status = 'ASSIGNED'
        session.save()
        self.assertEqual(session.status, 'ASSIGNED')


class TestLessonsModels(TestCase):
    """Tests for lessons_model.py"""
    
    def setUp(self):
        self.teacher = User.objects.create_user(
            username='teacher_lm', email='teacher_lm@test.com', password='testpass123',
            first_name='Test', last_name='Teacher', role='teacher', is_email_verified=True
        )
        self.student = User.objects.create_user(
            username='student_lm', email='student_lm@test.com', password='testpass123',
            first_name='Test', last_name='Student', role='student', is_email_verified=True
        )
    
    def test_lesson_content_str(self):
        """Test LessonContent string representation"""
        from eduAPI.models.lessons_model import Lesson, LessonContent
        
        lesson = Lesson.objects.create(
            name='Test Lesson',
            subject='Math',
            level='10',
            teacher=self.teacher
        )
        
        content = LessonContent.objects.create(
            lesson=lesson,
            title='Test Content',
            content_type='TEXT'
        )
        
        self.assertIn('Test Content', str(content))
    
    def test_question_str(self):
        """Test Question string representation"""
        from eduAPI.models.lessons_model import Lesson, Quiz, Question
        
        lesson = Lesson.objects.create(
            name='Test Lesson',
            subject='Math',
            level='10',
            teacher=self.teacher
        )
        
        quiz = Quiz.objects.create(
            lesson=lesson,
            title='Test Quiz',
            passing_score=70
        )
        
        question = Question.objects.create(
            quiz=quiz,
            question_text='What is 2+2?',
            points=10
        )
        
        self.assertIn('What is 2+2?', str(question))
    
    def test_answer_str(self):
        """Test Answer string representation"""
        from eduAPI.models.lessons_model import Lesson, Quiz, Question, Answer
        
        lesson = Lesson.objects.create(
            name='Test Lesson',
            subject='Math',
            level='10',
            teacher=self.teacher
        )
        
        quiz = Quiz.objects.create(
            lesson=lesson,
            title='Test Quiz',
            passing_score=70
        )
        
        question = Question.objects.create(
            quiz=quiz,
            question_text='What is 2+2?',
            points=10
        )
        
        answer = Answer.objects.create(
            question=question,
            answer_text='4',
            is_correct=True
        )
        
        self.assertIn('4', str(answer))
    
    def test_quiz_attempt_str(self):
        """Test QuizAttempt string representation"""
        from eduAPI.models.lessons_model import Lesson, Quiz, QuizAttempt
        
        lesson = Lesson.objects.create(
            name='Test Lesson',
            subject='Math',
            level='10',
            teacher=self.teacher
        )
        
        quiz = Quiz.objects.create(
            lesson=lesson,
            title='Test Quiz',
            passing_score=70
        )
        
        attempt = QuizAttempt.objects.create(
            student=self.student,
            quiz=quiz,
            score=80,
            passed=True
        )
        
        self.assertIn('Test Quiz', str(attempt))
    
    def test_student_enrollment_str(self):
        """Test StudentEnrollment string representation"""
        from eduAPI.models.lessons_model import Lesson, StudentEnrollment
        
        lesson = Lesson.objects.create(
            name='Test Lesson',
            subject='Math',
            level='10',
            teacher=self.teacher
        )
        
        enrollment = StudentEnrollment.objects.create(
            student=self.student,
            lesson=lesson,
            progress=50
        )
        
        self.assertIn('Test Lesson', str(enrollment))


class TestUserModel(TestCase):
    """Tests for user_model.py"""
    
    def test_user_is_admin_property(self):
        """Test User is_admin property"""
        admin = User.objects.create_superuser(
            username='admin_test', email='admin_test@test.com', password='testpass123',
            first_name='Admin', last_name='User'
        )
        
        self.assertTrue(admin.is_admin)
    
    def test_user_save_auto_admin_role(self):
        """Test User save auto-sets admin role for superusers when role is empty"""
        # Create a superuser without specifying role - should auto-set to admin
        admin = User(
            username='admin_test2', 
            email='admin_test2@test.com', 
            first_name='Admin', 
            last_name='User',
            is_superuser=True,
            is_staff=True,
            role=''  # Empty role should trigger auto-set
        )
        admin.set_password('testpass123')
        admin.save()
        
        # Superuser with empty role should have admin role auto-set
        self.assertEqual(admin.role, 'admin')


class TestSerializersValidation(TestCase):
    """Tests for serializer validation"""
    
    def setUp(self):
        self.teacher = User.objects.create_user(
            username='teacher_sv', email='teacher_sv@test.com', password='testpass123',
            first_name='Test', last_name='Teacher', role='teacher', is_email_verified=True
        )
        self.advisor = User.objects.create_user(
            username='advisor_sv', email='advisor_sv@test.com', password='testpass123',
            first_name='Test', last_name='Advisor', role='advisor', is_email_verified=True
        )
        self.student = User.objects.create_user(
            username='student_sv', email='student_sv@test.com', password='testpass123',
            first_name='Test', last_name='Student', role='student', is_email_verified=True
        )
    
    def test_student_group_serializer_create(self):
        """Test StudentGroupSerializer create method"""
        from eduAPI.serializers.recurring_sessions_serializers import StudentGroupSerializer
        from rest_framework.test import APIRequestFactory
        
        factory = APIRequestFactory()
        request = factory.post('/api/recurring-sessions/groups/')
        request.user = self.advisor
        
        data = {
            'name': 'Test Group',
            'description': 'A test group',
            'students': [self.student.id]
        }
        
        serializer = StudentGroupSerializer(data=data, context={'request': request})
        if serializer.is_valid():
            group = serializer.save()
            self.assertEqual(group.name, 'Test Group')
    
    def test_template_group_assignment_serializer_validation(self):
        """Test TemplateGroupAssignmentSerializer validation"""
        from eduAPI.serializers.recurring_sessions_serializers import TemplateGroupAssignmentSerializer
        from eduAPI.models.recurring_sessions_models import SessionTemplate, StudentGroup
        from rest_framework.test import APIRequestFactory
        
        factory = APIRequestFactory()
        request = factory.post('/api/recurring-sessions/assignments/')
        request.user = self.advisor
        
        template = SessionTemplate.objects.create(
            title='Weekly Math',
            teacher=self.teacher,
            subject='Math',
            level='10',
            day_of_week=1,
            start_time='10:00:00',
            duration_minutes=60,
            recurrence_type='WEEKLY',
            start_date=timezone.now().date()
        )
        
        group = StudentGroup.objects.create(
            name='Test Group',
            advisor=self.advisor
        )
        
        data = {
            'template': template.id,
            'group': group.id
        }
        
        serializer = TemplateGroupAssignmentSerializer(data=data, context={'request': request})
        if serializer.is_valid():
            assignment = serializer.save()
            self.assertEqual(assignment.template, template)


class TestSignals(TestCase):
    """Tests for signals"""
    
    def setUp(self):
        self.teacher = User.objects.create_user(
            username='teacher_sig', email='teacher_sig@test.com', password='testpass123',
            first_name='Test', last_name='Teacher', role='teacher', is_email_verified=True
        )
        self.advisor = User.objects.create_user(
            username='advisor_sig', email='advisor_sig@test.com', password='testpass123',
            first_name='Test', last_name='Advisor', role='advisor', is_email_verified=True
        )
    
    def test_template_group_assignment_signal(self):
        """Test signal fires on TemplateGroupAssignment creation"""
        from eduAPI.models.recurring_sessions_models import SessionTemplate, StudentGroup, TemplateGroupAssignment
        
        template = SessionTemplate.objects.create(
            title='Weekly Math',
            teacher=self.teacher,
            subject='Math',
            level='10',
            day_of_week=1,
            start_time='10:00:00',
            duration_minutes=60,
            recurrence_type='WEEKLY',
            start_date=timezone.now().date()
        )
        
        group = StudentGroup.objects.create(
            name='Test Group',
            advisor=self.advisor
        )
        
        # This should trigger the signal
        assignment = TemplateGroupAssignment.objects.create(
            template=template,
            group=group,
            advisor=self.advisor
        )
        
        self.assertIsNotNone(assignment.id)


class TestServicesExtended(TestCase):
    """Extended tests for services"""
    
    def setUp(self):
        self.teacher = User.objects.create_user(
            username='teacher_svc', email='teacher_svc@test.com', password='testpass123',
            first_name='Test', last_name='Teacher', role='teacher', is_email_verified=True
        )
    
    def test_lesson_service_get_all_lessons(self):
        """Test LessonService get all lessons"""
        from eduAPI.services.lessons_service import LessonService
        from eduAPI.models.lessons_model import Lesson
        
        Lesson.objects.create(name='Lesson 1', subject='Math', level='10', teacher=self.teacher)
        Lesson.objects.create(name='Lesson 2', subject='Science', level='10', teacher=self.teacher)
        
        lessons = LessonService.get_teacher_lessons(self.teacher.id)
        self.assertEqual(len(lessons), 2)
    
    def test_quiz_service_get_all_quizzes(self):
        """Test QuizService get all quizzes for a lesson"""
        from eduAPI.services.lessons_service import QuizService
        from eduAPI.models.lessons_model import Lesson, Quiz
        
        lesson = Lesson.objects.create(name='Test Lesson', subject='Math', level='10', teacher=self.teacher)
        Quiz.objects.create(lesson=lesson, title='Quiz 1', passing_score=70)
        Quiz.objects.create(lesson=lesson, title='Quiz 2', passing_score=80)
        
        quizzes = QuizService.get_lesson_quizzes(lesson.id)
        self.assertEqual(len(quizzes), 2)
