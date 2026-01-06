"""
Comprehensive tests for session_generator.py service
Target: Increase coverage from 31% to 80%+
"""
import pytest
from datetime import datetime, timedelta, date, time
from unittest.mock import patch, MagicMock
from django.test import TestCase
from django.utils import timezone
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.mark.django_db
class TestSessionGeneratorService:
    """Tests for SessionGeneratorService"""
    
    @pytest.fixture(autouse=True)
    def setup(self, teacher_user, db):
        self.teacher = teacher_user
        
        try:
            from eduAPI.services.session_generator import SessionGeneratorService
            from eduAPI.models.recurring_sessions_models import SessionTemplate, StudentGroup
            from eduAPI.models.live_sessions_models import LiveSession
            
            self.SessionGeneratorService = SessionGeneratorService
            self.SessionTemplate = SessionTemplate
            self.StudentGroup = StudentGroup
            self.LiveSession = LiveSession
            
        except ImportError:
            pytest.skip("Required models not available")
    
    def test_init(self):
        """Test service initialization"""
        generator = self.SessionGeneratorService()
        assert generator.generated_count == 0
        assert generator.failed_count == 0
        assert generator.skipped_count == 0
    
    def test_generate_sessions_for_date_no_templates(self):
        """Test generation when no templates exist"""
        generator = self.SessionGeneratorService()
        result = generator.generate_sessions_for_date()
        
        assert 'generated' in result
        assert 'failed' in result
        assert 'skipped' in result
        assert result['generated'] == 0
    
    def test_generate_sessions_for_specific_date(self):
        """Test generation for specific date"""
        generator = self.SessionGeneratorService()
        target_date = date(2025, 6, 15)
        result = generator.generate_sessions_for_date(target_date)
        
        assert result['date'] == target_date
    
    def test_should_generate_session_no_assignments(self):
        """Test should_generate_session returns False when no assignments"""
        generator = self.SessionGeneratorService()
        
        # Create template without assignments
        template = self.SessionTemplate.objects.create(
            title='Test Template',
            subject='Math',
            level='10',
            teacher=self.teacher,
            day_of_week=0,  # Monday
            start_time=time(10, 0),
            duration_minutes=60,
            recurrence_type='WEEKLY',
            start_date=date.today()
        )
        
        result = generator.should_generate_session(template, date.today())
        assert result is False
    
    def test_date_matches_template_schedule_wrong_day(self):
        """Test date_matches_template_schedule returns False for wrong day"""
        generator = self.SessionGeneratorService()
        
        template = self.SessionTemplate.objects.create(
            title='Test Template',
            subject='Math',
            level='10',
            teacher=self.teacher,
            day_of_week=0,  # Monday
            start_time=time(10, 0),
            duration_minutes=60,
            recurrence_type='WEEKLY',
            start_date=date.today()
        )
        
        # Use a Tuesday
        tuesday = date(2025, 1, 7)  # This is a Tuesday
        result = generator.date_matches_template_schedule(template, tuesday)
        assert result is False
    
    def test_date_matches_template_schedule_before_start(self):
        """Test date_matches_template_schedule returns False before start date"""
        generator = self.SessionGeneratorService()
        
        future_date = date.today() + timedelta(days=30)
        template = self.SessionTemplate.objects.create(
            title='Test Template',
            subject='Math',
            level='10',
            teacher=self.teacher,
            day_of_week=future_date.weekday(),
            start_time=time(10, 0),
            duration_minutes=60,
            recurrence_type='WEEKLY',
            start_date=future_date
        )
        
        past_date = date.today() - timedelta(days=7)
        result = generator.date_matches_template_schedule(template, past_date)
        assert result is False
    
    def test_date_matches_template_schedule_weekly(self):
        """Test date_matches_template_schedule for weekly recurrence"""
        generator = self.SessionGeneratorService()
        
        # Find next Monday
        today = date.today()
        days_until_monday = (7 - today.weekday()) % 7
        if days_until_monday == 0:
            days_until_monday = 7
        next_monday = today + timedelta(days=days_until_monday)
        
        template = self.SessionTemplate.objects.create(
            title='Test Template',
            subject='Math',
            level='10',
            teacher=self.teacher,
            day_of_week=0,  # Monday
            start_time=time(10, 0),
            duration_minutes=60,
            recurrence_type='WEEKLY',
            start_date=today - timedelta(days=30)
        )
        
        result = generator.date_matches_template_schedule(template, next_monday)
        assert result is True
    
    def test_date_matches_template_schedule_biweekly(self):
        """Test date_matches_template_schedule for biweekly recurrence"""
        generator = self.SessionGeneratorService()
        
        today = date.today()
        template = self.SessionTemplate.objects.create(
            title='Test Template',
            subject='Math',
            level='10',
            teacher=self.teacher,
            day_of_week=today.weekday(),
            start_time=time(10, 0),
            duration_minutes=60,
            recurrence_type='BIWEEKLY',
            start_date=today - timedelta(days=30),
            last_generated=today - timedelta(days=7)  # Only 1 week ago
        )
        
        result = generator.date_matches_template_schedule(template, today)
        assert result is False  # Should be False because only 7 days passed
    
    def test_date_matches_template_schedule_monthly(self):
        """Test date_matches_template_schedule for monthly recurrence"""
        generator = self.SessionGeneratorService()
        
        today = date.today()
        template = self.SessionTemplate.objects.create(
            title='Test Template',
            subject='Math',
            level='10',
            teacher=self.teacher,
            day_of_week=today.weekday(),
            start_time=time(10, 0),
            duration_minutes=60,
            recurrence_type='MONTHLY',
            start_date=today - timedelta(days=60),
            last_generated=today - timedelta(days=14)  # Only 2 weeks ago
        )
        
        result = generator.date_matches_template_schedule(template, today)
        assert result is False  # Should be False because only 14 days passed
    
    def test_cleanup_old_logs(self):
        """Test cleanup_old_logs removes old entries"""
        generator = self.SessionGeneratorService()
        deleted_count = generator.cleanup_old_logs(days_to_keep=30)
        assert deleted_count >= 0
    
    def test_generate_upcoming_sessions(self):
        """Test generate_upcoming_sessions for multiple days"""
        generator = self.SessionGeneratorService()
        results = generator.generate_upcoming_sessions(days_ahead=3)
        
        assert len(results) == 3
        for result in results:
            assert 'generated' in result
            assert 'failed' in result
            assert 'skipped' in result


@pytest.mark.django_db
class TestConvenienceFunctions:
    """Tests for convenience functions"""
    
    def test_generate_sessions_for_today(self):
        """Test generate_sessions_for_today function"""
        from eduAPI.services.session_generator import generate_sessions_for_today
        
        result = generate_sessions_for_today()
        assert 'generated' in result
        assert 'failed' in result
    
    def test_generate_sessions_for_week(self):
        """Test generate_sessions_for_week function"""
        from eduAPI.services.session_generator import generate_sessions_for_week
        
        results = generate_sessions_for_week()
        assert len(results) == 7
    
    def test_generate_sessions_for_date_function(self):
        """Test generate_sessions_for_date function"""
        from eduAPI.services.session_generator import generate_sessions_for_date
        
        target_date = date(2025, 6, 15)
        result = generate_sessions_for_date(target_date)
        assert result['date'] == target_date


@pytest.mark.django_db
class TestSessionCreation:
    """Tests for session creation from templates"""
    
    @pytest.fixture(autouse=True)
    def setup(self, teacher_user, student_user, advisor_user, db):
        self.teacher = teacher_user
        self.student = student_user
        self.advisor = advisor_user
        
        try:
            from eduAPI.services.session_generator import SessionGeneratorService
            from eduAPI.models.recurring_sessions_models import (
                SessionTemplate, StudentGroup, TemplateGroupAssignment
            )
            from eduAPI.models.live_sessions_models import LiveSession
            
            self.SessionGeneratorService = SessionGeneratorService
            self.SessionTemplate = SessionTemplate
            self.StudentGroup = StudentGroup
            self.TemplateGroupAssignment = TemplateGroupAssignment
            self.LiveSession = LiveSession
            
        except ImportError:
            pytest.skip("Required models not available")
    
    def test_create_session_from_template(self):
        """Test creating a session from template"""
        generator = self.SessionGeneratorService()
        
        today = date.today()
        
        # Create template
        template = self.SessionTemplate.objects.create(
            title='Test Session Template',
            subject='Math',
            level='10',
            teacher=self.teacher,
            day_of_week=today.weekday(),
            start_time=time(10, 0),
            duration_minutes=60,
            recurrence_type='WEEKLY',
            start_date=today
        )
        
        # Create student group
        group = self.StudentGroup.objects.create(
            name='Test Group',
            advisor=self.advisor
        )
        group.students.add(self.student)
        
        # Create assignment
        assignment = self.TemplateGroupAssignment.objects.create(
            template=template,
            group=group,
            advisor=self.advisor,
            is_active=True
        )
        
        # Generate session
        session = generator.create_session_from_template(template, today)
        
        assert session is not None
        assert session.title == template.title
        assert session.teacher == self.teacher
    
    def test_log_generation_attempt(self):
        """Test logging generation attempts"""
        generator = self.SessionGeneratorService()
        
        today = date.today()
        template = self.SessionTemplate.objects.create(
            title='Test Template',
            subject='Math',
            level='10',
            teacher=self.teacher,
            day_of_week=today.weekday(),
            start_time=time(10, 0),
            duration_minutes=60,
            recurrence_type='WEEKLY',
            start_date=today
        )
        
        # Log attempt
        generator.log_generation_attempt(
            template,
            today,
            'SUCCESS',
            'Test message'
        )
        
        from eduAPI.models.recurring_sessions_models import TemplateGenerationLog
        logs = TemplateGenerationLog.objects.filter(template=template)
        assert logs.count() >= 1
