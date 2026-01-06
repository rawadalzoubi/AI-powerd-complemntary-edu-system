# Tests for admin_views.py to increase coverage
import pytest
import json
from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from django.contrib.admin.sites import AdminSite
from django.contrib.messages.storage.fallback import FallbackStorage
from django.contrib.sessions.middleware import SessionMiddleware
from unittest.mock import patch, MagicMock

User = get_user_model()


class TestAdminViews(TestCase):
    """Tests for admin_views.py"""
    
    def setUp(self):
        self.factory = RequestFactory()
        self.superuser = User.objects.create_superuser(
            username='admin_av1',
            email='admin@test.com',
            password='testpass123',
            first_name='Admin',
            last_name='User'
        )
        self.advisor = User.objects.create_user(
            username='advisor_av1',
            email='advisor@test.com',
            password='testpass123',
            first_name='Test',
            last_name='Advisor',
            role='advisor',
            is_email_verified=True
        )
    
    def _add_middleware(self, request):
        """Add session and messages middleware to request"""
        middleware = SessionMiddleware(lambda x: None)
        middleware.process_request(request)
        request.session.save()
        
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)
        
        return request
    
    @patch('eduAPI.views.admin_views.redirect')
    def test_reset_advisor_password_success(self, mock_redirect):
        """Test successful password reset"""
        from eduAPI.views.admin_views import reset_advisor_password
        from django.http import HttpResponseRedirect
        
        mock_redirect.return_value = HttpResponseRedirect('/admin/')
        
        request = self.factory.post(f'/admin/reset-password/{self.advisor.id}/')
        request.user = self.superuser
        request = self._add_middleware(request)
        
        response = reset_advisor_password(request, self.advisor.id)
        
        # Should redirect
        self.assertEqual(response.status_code, 302)
    
    @patch('eduAPI.views.admin_views.redirect')
    def test_reset_advisor_password_not_found(self, mock_redirect):
        """Test password reset for non-existent user"""
        from eduAPI.views.admin_views import reset_advisor_password
        from django.http import HttpResponseRedirect
        
        mock_redirect.return_value = HttpResponseRedirect('/admin/')
        
        request = self.factory.post('/admin/reset-password/99999/')
        request.user = self.superuser
        request = self._add_middleware(request)
        
        response = reset_advisor_password(request, 99999)
        
        # Should redirect with error
        self.assertEqual(response.status_code, 302)
    
    def test_advisor_stats(self):
        """Test advisor statistics endpoint"""
        from eduAPI.views.admin_views import advisor_stats
        
        request = self.factory.get('/admin/advisor-stats/')
        request.user = self.superuser
        
        response = advisor_stats(request)
        
        self.assertEqual(response.status_code, 200)
        # JsonResponse content needs to be decoded
        data = json.loads(response.content)
        self.assertIn('total_advisors', data)
        self.assertIn('active_advisors', data)
        self.assertIn('inactive_advisors', data)


class TestModelsExtendedCoverage(TestCase):
    """Extended tests for models to increase coverage"""
    
    def setUp(self):
        self.teacher = User.objects.create_user(
            username='teacher_mc1',
            email='teacher@test.com',
            password='testpass123',
            first_name='Test',
            last_name='Teacher',
            role='teacher',
            is_email_verified=True
        )
        self.student = User.objects.create_user(
            username='student_mc1',
            email='student@test.com',
            password='testpass123',
            first_name='Test',
            last_name='Student',
            role='student',
            is_email_verified=True
        )
        self.advisor = User.objects.create_user(
            username='advisor_mc1',
            email='advisor@test.com',
            password='testpass123',
            first_name='Test',
            last_name='Advisor',
            role='advisor',
            is_email_verified=True
        )
    
    def test_user_full_name(self):
        """Test User.get_full_name()"""
        self.assertEqual(self.teacher.get_full_name(), 'Test Teacher')
    
    def test_user_str(self):
        """Test User.__str__()"""
        self.assertEqual(str(self.teacher), 'teacher@test.com')
    
    def test_lesson_str(self):
        """Test Lesson.__str__()"""
        from eduAPI.models.lessons_model import Lesson
        
        lesson = Lesson.objects.create(
            name='Test Lesson',
            subject='Math',
            level='10',
            teacher=self.teacher
        )
        
        # Actual format: "Test Lesson - Math (Grade 10)"
        self.assertEqual(str(lesson), 'Test Lesson - Math (Grade 10)')
    
    def test_quiz_str(self):
        """Test Quiz.__str__()"""
        from eduAPI.models.lessons_model import Lesson, Quiz
        
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
        
        # Actual format: "Test Quiz - Test Lesson"
        self.assertEqual(str(quiz), 'Test Quiz - Test Lesson')
    
    def test_live_session_str(self):
        """Test LiveSession.__str__()"""
        from eduAPI.models.live_sessions_models import LiveSession
        from django.utils import timezone
        from datetime import timedelta
        
        session = LiveSession.objects.create(
            title='Test Session',
            teacher=self.teacher,
            subject='Math',
            level='10',
            scheduled_datetime=timezone.now() + timedelta(hours=1),
            duration_minutes=60
        )
        
        self.assertIn('Test Session', str(session))
    
    def test_session_template_str(self):
        """Test SessionTemplate.__str__()"""
        from eduAPI.models.recurring_sessions_models import SessionTemplate
        from django.utils import timezone
        
        template = SessionTemplate.objects.create(
            title='Test Template',
            teacher=self.teacher,
            subject='Math',
            level='10',
            day_of_week=1,
            start_time='10:00:00',
            recurrence_type='WEEKLY',
            status='ACTIVE',
            start_date=timezone.now().date()
        )
        
        self.assertIn('Test Template', str(template))
    
    def test_student_group_str(self):
        """Test StudentGroup.__str__()"""
        from eduAPI.models.recurring_sessions_models import StudentGroup
        
        group = StudentGroup.objects.create(
            name='Test Group',
            advisor=self.advisor,
            is_active=True
        )
        
        # Actual format: "Test Group (0 students)"
        self.assertEqual(str(group), 'Test Group (0 students)')
    
    def test_student_group_student_count(self):
        """Test StudentGroup.student_count property"""
        from eduAPI.models.recurring_sessions_models import StudentGroup
        
        group = StudentGroup.objects.create(
            name='Test Group',
            advisor=self.advisor,
            is_active=True
        )
        group.students.add(self.student)
        
        self.assertEqual(group.student_count, 1)


class TestSerializersExtendedCoverage(TestCase):
    """Extended tests for serializers to increase coverage"""
    
    def setUp(self):
        self.teacher = User.objects.create_user(
            username='teacher_sc1',
            email='teacher@test.com',
            password='testpass123',
            first_name='Test',
            last_name='Teacher',
            role='teacher',
            is_email_verified=True
        )
    
    def test_lesson_serializer(self):
        """Test LessonSerializer"""
        from eduAPI.models.lessons_model import Lesson
        from eduAPI.serializers.lessons_serializers import LessonSerializer
        
        lesson = Lesson.objects.create(
            name='Test Lesson',
            subject='Math',
            level='10',
            teacher=self.teacher
        )
        
        serializer = LessonSerializer(lesson)
        data = serializer.data
        
        self.assertEqual(data['name'], 'Test Lesson')
        self.assertEqual(data['subject'], 'Math')
    
    def test_quiz_serializer(self):
        """Test QuizSerializer"""
        from eduAPI.models.lessons_model import Lesson, Quiz
        from eduAPI.serializers.lessons_serializers import QuizSerializer
        
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
        
        serializer = QuizSerializer(quiz)
        data = serializer.data
        
        self.assertEqual(data['title'], 'Test Quiz')
        self.assertEqual(data['passing_score'], 70)


class TestMiddlewareCoverage(TestCase):
    """Tests for middleware.py"""
    
    def test_middleware_process_request(self):
        """Test DisableCSRFMiddleware processes request"""
        from eduAPI.middleware import DisableCSRFMiddleware
        from django.test import RequestFactory
        from django.conf import settings
        
        factory = RequestFactory()
        request = factory.get('/api/test/')
        
        def get_response(request):
            from django.http import HttpResponse
            return HttpResponse('OK')
        
        middleware = DisableCSRFMiddleware(get_response)
        response = middleware(request)
        
        self.assertEqual(response.status_code, 200)
    
    def test_middleware_csrf_exempt(self):
        """Test DisableCSRFMiddleware with CSRF exempt URL"""
        from eduAPI.middleware import DisableCSRFMiddleware
        from django.test import RequestFactory, override_settings
        
        factory = RequestFactory()
        request = factory.post('/api/test/')
        
        def get_response(request):
            from django.http import HttpResponse
            return HttpResponse('OK')
        
        with override_settings(CSRF_EXEMPT_URLS=[r'^/api/.*$']):
            middleware = DisableCSRFMiddleware(get_response)
            middleware.process_request(request)
            
            # Check that CSRF check is disabled
            self.assertTrue(getattr(request, '_dont_enforce_csrf_checks', False))


class TestSignalsCoverage(TestCase):
    """Tests for signals"""
    
    def setUp(self):
        self.teacher = User.objects.create_user(
            username='teacher_sig1',
            email='teacher@test.com',
            password='testpass123',
            first_name='Test',
            last_name='Teacher',
            role='teacher',
            is_email_verified=True
        )
        self.advisor = User.objects.create_user(
            username='advisor_sig1',
            email='advisor@test.com',
            password='testpass123',
            first_name='Test',
            last_name='Advisor',
            role='advisor',
            is_email_verified=True
        )
    
    def test_template_group_assignment_signal(self):
        """Test signal when template group assignment is created"""
        from eduAPI.models.recurring_sessions_models import SessionTemplate, StudentGroup, TemplateGroupAssignment
        from django.utils import timezone
        
        template = SessionTemplate.objects.create(
            title='Test Template',
            teacher=self.teacher,
            subject='Math',
            level='10',
            day_of_week=1,
            start_time='10:00:00',
            recurrence_type='WEEKLY',
            status='ACTIVE',
            start_date=timezone.now().date()
        )
        
        group = StudentGroup.objects.create(
            name='Test Group',
            advisor=self.advisor,
            is_active=True
        )
        
        # This should trigger the signal
        assignment = TemplateGroupAssignment.objects.create(
            template=template,
            group=group,
            advisor=self.advisor,
            is_active=True
        )
        
        self.assertIsNotNone(assignment.id)
