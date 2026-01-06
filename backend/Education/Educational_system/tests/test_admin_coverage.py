# Tests for admin modules to increase coverage
import pytest
from django.test import TestCase, RequestFactory
from django.contrib.admin.sites import AdminSite
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from unittest.mock import Mock, patch, MagicMock

User = get_user_model()


class TestRecurringSessionsAdmin(TestCase):
    """Tests for recurring_sessions_admin.py"""
    
    def setUp(self):
        self.factory = RequestFactory()
        self.site = AdminSite()
        self.teacher = User.objects.create_user(
            username='teacher_admin',
            email='teacher@test.com',
            password='testpass123',
            first_name='Test',
            last_name='Teacher',
            role='teacher'
        )
        self.advisor = User.objects.create_user(
            username='advisor_admin',
            email='advisor@test.com',
            password='testpass123',
            first_name='Test',
            last_name='Advisor',
            role='advisor'
        )
        self.student = User.objects.create_user(
            username='student_admin',
            email='student@test.com',
            password='testpass123',
            first_name='Test',
            last_name='Student',
            role='student'
        )
    
    def test_session_template_admin_list_display(self):
        """Test SessionTemplateAdmin list display"""
        from eduAPI.admin.recurring_sessions_admin import SessionTemplateAdmin
        from eduAPI.models.recurring_sessions_models import SessionTemplate
        
        admin = SessionTemplateAdmin(SessionTemplate, self.site)
        
        # Check list_display fields
        expected_fields = [
            'title', 'teacher', 'subject', 'level', 'day_of_week',
            'start_time', 'recurrence_type', 'status', 'total_generated',
            'next_generation_date', 'created_at'
        ]
        for field in expected_fields:
            self.assertIn(field, admin.list_display)
    
    def test_session_template_admin_list_filter(self):
        """Test SessionTemplateAdmin list filter"""
        from eduAPI.admin.recurring_sessions_admin import SessionTemplateAdmin
        from eduAPI.models.recurring_sessions_models import SessionTemplate
        
        admin = SessionTemplateAdmin(SessionTemplate, self.site)
        
        expected_filters = ['status', 'recurrence_type', 'day_of_week', 'subject', 'level', 'created_at']
        for filter_field in expected_filters:
            self.assertIn(filter_field, admin.list_filter)
    
    def test_session_template_admin_actions(self):
        """Test SessionTemplateAdmin actions"""
        from eduAPI.admin.recurring_sessions_admin import SessionTemplateAdmin
        from eduAPI.models.recurring_sessions_models import SessionTemplate
        
        admin = SessionTemplateAdmin(SessionTemplate, self.site)
        
        # Check actions exist
        self.assertIn('pause_templates', admin.actions)
        self.assertIn('resume_templates', admin.actions)
        self.assertIn('end_templates', admin.actions)
    
    def test_session_template_admin_pause_action(self):
        """Test pause_templates action"""
        from eduAPI.admin.recurring_sessions_admin import SessionTemplateAdmin
        from eduAPI.models.recurring_sessions_models import SessionTemplate
        
        # Create a template
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
        
        admin = SessionTemplateAdmin(SessionTemplate, self.site)
        request = self.factory.post('/')
        request.user = self.teacher
        
        # Mock message_user
        admin.message_user = Mock()
        
        queryset = SessionTemplate.objects.filter(id=template.id)
        admin.pause_templates(request, queryset)
        
        template.refresh_from_db()
        self.assertEqual(template.status, 'PAUSED')
    
    def test_session_template_admin_resume_action(self):
        """Test resume_templates action"""
        from eduAPI.admin.recurring_sessions_admin import SessionTemplateAdmin
        from eduAPI.models.recurring_sessions_models import SessionTemplate
        
        template = SessionTemplate.objects.create(
            title='Test Template',
            teacher=self.teacher,
            subject='Math',
            level='10',
            day_of_week=1,
            start_time='10:00:00',
            recurrence_type='WEEKLY',
            status='PAUSED',
            start_date=timezone.now().date()
        )
        
        admin = SessionTemplateAdmin(SessionTemplate, self.site)
        request = self.factory.post('/')
        request.user = self.teacher
        admin.message_user = Mock()
        
        queryset = SessionTemplate.objects.filter(id=template.id)
        admin.resume_templates(request, queryset)
        
        template.refresh_from_db()
        self.assertEqual(template.status, 'ACTIVE')
    
    def test_session_template_admin_end_action(self):
        """Test end_templates action"""
        from eduAPI.admin.recurring_sessions_admin import SessionTemplateAdmin
        from eduAPI.models.recurring_sessions_models import SessionTemplate
        
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
        
        admin = SessionTemplateAdmin(SessionTemplate, self.site)
        request = self.factory.post('/')
        request.user = self.teacher
        admin.message_user = Mock()
        
        queryset = SessionTemplate.objects.filter(id=template.id)
        admin.end_templates(request, queryset)
        
        template.refresh_from_db()
        self.assertEqual(template.status, 'ENDED')
    
    def test_session_template_admin_next_generation_date(self):
        """Test next_generation_date method"""
        from eduAPI.admin.recurring_sessions_admin import SessionTemplateAdmin
        from eduAPI.models.recurring_sessions_models import SessionTemplate
        
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
        
        admin = SessionTemplateAdmin(SessionTemplate, self.site)
        result = admin.next_generation_date(template)
        
        # Should return a date string or '-'
        self.assertIsNotNone(result)
    
    def test_student_group_admin_list_display(self):
        """Test StudentGroupAdmin list display"""
        from eduAPI.admin.recurring_sessions_admin import StudentGroupAdmin
        from eduAPI.models.recurring_sessions_models import StudentGroup
        
        admin = StudentGroupAdmin(StudentGroup, self.site)
        
        expected_fields = ['name', 'advisor', 'student_count', 'is_active', 'template_assignments_count', 'created_at']
        for field in expected_fields:
            self.assertIn(field, admin.list_display)
    
    def test_student_group_admin_student_count(self):
        """Test student_count method"""
        from eduAPI.admin.recurring_sessions_admin import StudentGroupAdmin
        from eduAPI.models.recurring_sessions_models import StudentGroup
        
        group = StudentGroup.objects.create(
            name='Test Group',
            advisor=self.advisor,
            is_active=True
        )
        group.students.add(self.student)
        
        admin = StudentGroupAdmin(StudentGroup, self.site)
        count = admin.student_count(group)
        
        self.assertEqual(count, 1)
    
    def test_template_group_assignment_admin(self):
        """Test TemplateGroupAssignmentAdmin"""
        from eduAPI.admin.recurring_sessions_admin import TemplateGroupAssignmentAdmin
        from eduAPI.models.recurring_sessions_models import TemplateGroupAssignment
        
        admin = TemplateGroupAssignmentAdmin(TemplateGroupAssignment, self.site)
        
        expected_fields = ['template', 'group', 'advisor', 'is_active', 'sessions_generated', 'last_session_date', 'assigned_date']
        for field in expected_fields:
            self.assertIn(field, admin.list_display)
    
    def test_generated_session_admin(self):
        """Test GeneratedSessionAdmin"""
        from eduAPI.admin.recurring_sessions_admin import GeneratedSessionAdmin
        from eduAPI.models.recurring_sessions_models import GeneratedSession
        
        admin = GeneratedSessionAdmin(GeneratedSession, self.site)
        
        expected_fields = ['session_title', 'template', 'session_date', 'students_assigned', 'groups_assigned', 'generation_date', 'session_status']
        for field in expected_fields:
            self.assertIn(field, admin.list_display)
    
    def test_template_generation_log_admin(self):
        """Test TemplateGenerationLogAdmin"""
        from eduAPI.admin.recurring_sessions_admin import TemplateGenerationLogAdmin
        from eduAPI.models.recurring_sessions_models import TemplateGenerationLog
        
        admin = TemplateGenerationLogAdmin(TemplateGenerationLog, self.site)
        
        # Check has_add_permission returns False
        request = self.factory.get('/')
        self.assertFalse(admin.has_add_permission(request))
        
        # Check has_change_permission returns False
        self.assertFalse(admin.has_change_permission(request))


class TestLiveSessionsAdmin(TestCase):
    """Tests for admin_live_sessions.py"""
    
    def setUp(self):
        self.factory = RequestFactory()
        self.site = AdminSite()
        self.teacher = User.objects.create_user(
            username='teacher_live',
            email='teacher@test.com',
            password='testpass123',
            first_name='Test',
            last_name='Teacher',
            role='teacher'
        )
    
    def test_live_session_admin_list_display(self):
        """Test LiveSessionAdmin list display"""
        from eduAPI.admin_live_sessions import LiveSessionAdmin
        from eduAPI.models.live_sessions_models import LiveSession
        
        admin = LiveSessionAdmin(LiveSession, self.site)
        
        expected_fields = ['title', 'teacher', 'subject', 'level', 'scheduled_datetime', 'status', 'assigned_students_count']
        for field in expected_fields:
            self.assertIn(field, admin.list_display)
    
    def test_live_session_admin_assigned_students_count(self):
        """Test assigned_students_count method"""
        from eduAPI.admin_live_sessions import LiveSessionAdmin
        from eduAPI.models.live_sessions_models import LiveSession
        
        session = LiveSession.objects.create(
            title='Test Session',
            teacher=self.teacher,
            subject='Math',
            level='10',
            scheduled_datetime=timezone.now() + timedelta(days=1),
            duration_minutes=60
        )
        
        admin = LiveSessionAdmin(LiveSession, self.site)
        count = admin.assigned_students_count(session)
        
        self.assertEqual(count, 0)
    
    def test_live_session_assignment_admin(self):
        """Test LiveSessionAssignmentAdmin"""
        from eduAPI.admin_live_sessions import LiveSessionAssignmentAdmin
        from eduAPI.models.live_sessions_models import LiveSessionAssignment
        
        admin = LiveSessionAssignmentAdmin(LiveSessionAssignment, self.site)
        
        expected_fields = ['session', 'student', 'advisor', 'assigned_date', 'attended', 'attendance_percentage']
        for field in expected_fields:
            self.assertIn(field, admin.list_display)
    
    def test_live_session_material_admin(self):
        """Test LiveSessionMaterialAdmin"""
        from eduAPI.admin_live_sessions import LiveSessionMaterialAdmin
        from eduAPI.models.live_sessions_models import LiveSessionMaterial
        
        admin = LiveSessionMaterialAdmin(LiveSessionMaterial, self.site)
        
        expected_fields = ['title', 'session', 'content_type', 'uploaded_by', 'uploaded_at', 'is_public']
        for field in expected_fields:
            self.assertIn(field, admin.list_display)
    
    def test_live_session_note_admin(self):
        """Test LiveSessionNoteAdmin"""
        from eduAPI.admin_live_sessions import LiveSessionNoteAdmin
        from eduAPI.models.live_sessions_models import LiveSessionNote
        
        admin = LiveSessionNoteAdmin(LiveSessionNote, self.site)
        
        expected_fields = ['session', 'author', 'is_private', 'created_at']
        for field in expected_fields:
            self.assertIn(field, admin.list_display)
    
    def test_live_session_notification_admin(self):
        """Test LiveSessionNotificationAdmin"""
        from eduAPI.admin_live_sessions import LiveSessionNotificationAdmin
        from eduAPI.models.live_sessions_models import LiveSessionNotification
        
        admin = LiveSessionNotificationAdmin(LiveSessionNotification, self.site)
        
        expected_fields = ['title', 'recipient', 'notification_type', 'is_read', 'created_at']
        for field in expected_fields:
            self.assertIn(field, admin.list_display)
