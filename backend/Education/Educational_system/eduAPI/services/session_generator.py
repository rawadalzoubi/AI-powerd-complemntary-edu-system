# backend/Education/Educational_system/eduAPI/services/session_generator.py
# Service for generating sessions from templates

import uuid
from datetime import datetime, timedelta, date
from django.utils import timezone
from django.db import transaction
from django.core.exceptions import ValidationError

from ..models.recurring_sessions_models import (
    SessionTemplate,
    TemplateGroupAssignment,
    GeneratedSession,
    TemplateGenerationLog
)
from ..models.live_sessions_models import LiveSession, LiveSessionAssignment


class SessionGeneratorService:
    """Service for generating LiveSession instances from SessionTemplate"""
    
    def __init__(self):
        self.generated_count = 0
        self.failed_count = 0
        self.skipped_count = 0
    
    def generate_sessions_for_date(self, target_date=None):
        """
        Generate sessions for a specific date (default: today)
        Returns summary of generation results
        """
        if target_date is None:
            target_date = timezone.now().date()
        
        print(f"DEBUG: Generating sessions for date: {target_date}")
        
        # Reset counters
        self.generated_count = 0
        self.failed_count = 0
        self.skipped_count = 0
        
        # Get active templates that might need sessions
        active_templates = SessionTemplate.objects.filter(
            status='ACTIVE',
            start_date__lte=target_date
        ).exclude(
            end_date__lt=target_date
        )
        
        print(f"DEBUG: Found {active_templates.count()} active templates")
        
        for template in active_templates:
            try:
                if self.should_generate_session(template, target_date):
                    self.create_session_from_template(template, target_date)
                    self.generated_count += 1
                else:
                    self.skipped_count += 1
            except Exception as e:
                print(f"ERROR: Failed to generate session for template {template.id}: {str(e)}")
                self.log_generation_attempt(template, target_date, 'FAILED', str(e))
                self.failed_count += 1
        
        summary = {
            'date': target_date,
            'generated': self.generated_count,
            'failed': self.failed_count,
            'skipped': self.skipped_count,
            'total_processed': active_templates.count()
        }
        
        print(f"DEBUG: Generation summary: {summary}")
        return summary
    
    def should_generate_session(self, template, target_date):
        """
        Check if a session should be generated for this template on this date
        """
        # Check if we already generated a session for this date
        if GeneratedSession.objects.filter(
            template=template,
            session__scheduled_datetime__date=target_date
        ).exists():
            print(f"DEBUG: Session already exists for template {template.id} on {target_date}")
            return False
        
        # Check if the target date matches the template's schedule
        if not self.date_matches_template_schedule(template, target_date):
            return False
        
        # Check if template has any active group assignments
        if not template.group_assignments.filter(is_active=True).exists():
            print(f"DEBUG: Template {template.id} has no active group assignments")
            return False
        
        return True
    
    def date_matches_template_schedule(self, template, target_date):
        """
        Check if the target date matches the template's recurrence schedule
        """
        # Check day of week
        if target_date.weekday() != template.day_of_week:
            return False
        
        # Check if target date is before start date
        if target_date < template.start_date:
            return False
        
        # If no previous generation, allow generation on start date or any matching day after
        if not template.last_generated:
            return True
        
        # Check recurrence pattern
        if template.recurrence_type == 'WEEKLY':
            # For weekly, check if it's been at least a week since last generation
            days_since_last = (target_date - template.last_generated).days
            if days_since_last < 7:
                return False
        
        elif template.recurrence_type == 'BIWEEKLY':
            # For bi-weekly, check if it's been at least 2 weeks
            days_since_last = (target_date - template.last_generated).days
            if days_since_last < 14:
                return False
        
        elif template.recurrence_type == 'MONTHLY':
            # For monthly, check if it's been at least 4 weeks (28 days)
            days_since_last = (target_date - template.last_generated).days
            if days_since_last < 28:
                return False
        
        return True
    
    @transaction.atomic
    def create_session_from_template(self, template, session_date):
        """
        Create a LiveSession from a SessionTemplate
        """
        print(f"DEBUG: Creating session from template {template.id} for {session_date}")
        
        # Calculate session datetime
        session_datetime = timezone.make_aware(
            datetime.combine(session_date, template.start_time)
        )
        
        # Create unique room name
        room_name = f"template-{template.id}-{session_date.strftime('%Y%m%d')}-{uuid.uuid4().hex[:8]}"
        
        # Create LiveSession
        session = LiveSession.objects.create(
            title=template.title,
            description=template.description or f"Generated from template: {template.title}",
            subject=template.subject,
            level=template.level,
            teacher=template.teacher,
            scheduled_datetime=session_datetime,
            duration_minutes=template.duration_minutes,
            max_participants=template.max_participants,
            jitsi_room_name=room_name,
            status='PENDING'  # Will be updated to ASSIGNED when students are assigned
        )
        
        print(f"DEBUG: Created LiveSession {session.id}: {session.title}")
        
        # Create GeneratedSession tracking record
        generated_session = GeneratedSession.objects.create(
            template=template,
            session=session,
            generated_by='system'
        )
        
        # Auto-assign groups
        total_students_assigned = 0
        active_assignments = template.group_assignments.filter(is_active=True)
        
        for assignment in active_assignments:
            students_in_group = assignment.group.students.all()
            
            for student in students_in_group:
                # Create LiveSessionAssignment
                LiveSessionAssignment.objects.create(
                    session=session,
                    student=student,
                    advisor=assignment.advisor,
                    assignment_message=f"Auto-assigned from template: {template.title}"
                )
                total_students_assigned += 1
            
            # Update assignment tracking
            assignment.sessions_generated += 1
            assignment.last_session_date = session_date
            assignment.save()
        
        # Update session status to ASSIGNED if students were assigned
        if total_students_assigned > 0:
            session.status = 'ASSIGNED'
            session.save()
        
        # Update template tracking
        template.last_generated = session_date
        template.total_generated += 1
        template.save()
        
        # Update generated session tracking
        generated_session.students_assigned = total_students_assigned
        generated_session.groups_assigned = active_assignments.count()
        generated_session.save()
        
        # Log successful generation
        self.log_generation_attempt(
            template, 
            session_date, 
            'SUCCESS', 
            f"Generated session with {total_students_assigned} students assigned",
            session
        )
        
        print(f"DEBUG: Successfully generated session {session.id} with {total_students_assigned} students")
        
        return session
    
    def log_generation_attempt(self, template, attempted_date, status, message, session=None):
        """
        Log a generation attempt for debugging and monitoring
        """
        students_assigned = 0
        if session:
            students_assigned = session.assignments.count()
        
        TemplateGenerationLog.objects.create(
            template=template,
            attempted_date=attempted_date,
            status=status,
            message=message,
            session_created=session,
            students_assigned=students_assigned
        )
    
    def generate_upcoming_sessions(self, days_ahead=7):
        """
        Generate sessions for the next N days
        """
        today = timezone.now().date()
        results = []
        
        for i in range(days_ahead):
            target_date = today + timedelta(days=i)
            result = self.generate_sessions_for_date(target_date)
            results.append(result)
        
        return results
    
    def cleanup_old_logs(self, days_to_keep=30):
        """
        Clean up old generation logs to prevent database bloat
        """
        cutoff_date = timezone.now() - timedelta(days=days_to_keep)
        deleted_count = TemplateGenerationLog.objects.filter(
            created_at__lt=cutoff_date
        ).delete()[0]
        
        print(f"DEBUG: Cleaned up {deleted_count} old generation logs")
        return deleted_count


# Convenience functions
def generate_sessions_for_today():
    """Generate sessions for today"""
    generator = SessionGeneratorService()
    return generator.generate_sessions_for_date()


def generate_sessions_for_week():
    """Generate sessions for the next 7 days"""
    generator = SessionGeneratorService()
    return generator.generate_upcoming_sessions(7)


def generate_sessions_for_date(target_date):
    """Generate sessions for a specific date"""
    generator = SessionGeneratorService()
    return generator.generate_sessions_for_date(target_date)