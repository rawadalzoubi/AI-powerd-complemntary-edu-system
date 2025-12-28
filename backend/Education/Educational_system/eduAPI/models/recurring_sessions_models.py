# backend/Education/Educational_system/eduAPI/models/recurring_sessions_models.py
# Recurring Sessions Models - Template-based session generation system

from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from django.core.exceptions import ValidationError
from .live_sessions_models import LiveSession

User = get_user_model()

class SessionTemplate(models.Model):
    """
    Template for creating recurring live sessions.
    Teachers create templates that automatically generate LiveSession instances.
    """
    
    # Recurrence pattern choices
    RECURRENCE_CHOICES = [
        ('WEEKLY', 'Weekly'),
        ('BIWEEKLY', 'Bi-weekly'),
        ('MONTHLY', 'Monthly'),
    ]
    
    # Day of week choices (0=Monday, 6=Sunday)
    DAY_OF_WEEK_CHOICES = [
        (0, 'Monday'),
        (1, 'Tuesday'),
        (2, 'Wednesday'),
        (3, 'Thursday'),
        (4, 'Friday'),
        (5, 'Saturday'),
        (6, 'Sunday'),
    ]
    
    # Status choices
    STATUS_CHOICES = [
        ('ACTIVE', 'Active'),
        ('PAUSED', 'Paused'),
        ('ENDED', 'Ended'),
    ]
    
    # Grade choices (same as LiveSession)
    GRADE_CHOICES = [
        ('1', '1st Grade'),
        ('2', '2nd Grade'),
        ('3', '3rd Grade'),
        ('4', '4th Grade'),
        ('5', '5th Grade'),
        ('6', '6th Grade'),
        ('7', '7th Grade'),
        ('8', '8th Grade'),
        ('9', '9th Grade'),
        ('10', '10th Grade'),
        ('11', '11th Grade'),
        ('12', '12th Grade'),
    ]
    
    # Basic Information (similar to LiveSession)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    subject = models.CharField(max_length=255)
    level = models.CharField(max_length=2, choices=GRADE_CHOICES)
    
    # Teacher Relationship
    teacher = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='session_templates'
    )
    
    # Schedule Configuration
    day_of_week = models.IntegerField(choices=DAY_OF_WEEK_CHOICES)
    start_time = models.TimeField()
    duration_minutes = models.IntegerField(
        default=60,
        validators=[MinValueValidator(15), MaxValueValidator(240)]
    )
    
    # Recurrence Pattern
    recurrence_type = models.CharField(
        max_length=20, 
        choices=RECURRENCE_CHOICES,
        default='WEEKLY'
    )
    
    # Date Range
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    
    # Status
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='ACTIVE'
    )
    
    # Session Configuration
    max_participants = models.IntegerField(default=50)
    
    # Tracking
    last_generated = models.DateField(null=True, blank=True)
    total_generated = models.IntegerField(default=0)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['teacher', 'status']),
            models.Index(fields=['status', 'start_date']),
            models.Index(fields=['day_of_week', 'start_time']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.get_recurrence_type_display()} ({self.get_day_of_week_display()})"
    
    def clean(self):
        """Validate template data"""
        if self.end_date and self.end_date <= self.start_date:
            raise ValidationError("End date must be after start date")
        
        # Only validate start_date for new templates (not when updating existing ones)
        if not self.pk and self.start_date and self.start_date < timezone.now().date():
            raise ValidationError("Start date cannot be in the past")
    
    @property
    def is_active(self):
        """Check if template is currently active"""
        return self.status == 'ACTIVE'
    
    @property
    def next_generation_date(self):
        """Calculate the next date when a session should be generated"""
        from datetime import timedelta
        
        if not self.is_active:
            return None
        
        today = timezone.now().date()
        
        # If never generated before
        if not self.last_generated:
            # If start date is today or in the past, and today matches the day_of_week
            if self.start_date <= today and today.weekday() == self.day_of_week:
                return today
            # Otherwise, find the next matching day starting from start_date
            base_date = max(self.start_date, today)
            days_ahead = (self.day_of_week - base_date.weekday()) % 7
            if days_ahead == 0 and base_date > self.start_date:
                days_ahead = 7
            return base_date + timedelta(days=days_ahead)
        
        # If already generated, calculate next occurrence based on recurrence type
        base_date = self.last_generated
        
        if self.recurrence_type == 'WEEKLY':
            next_date = base_date + timedelta(weeks=1)
        elif self.recurrence_type == 'BIWEEKLY':
            next_date = base_date + timedelta(weeks=2)
        elif self.recurrence_type == 'MONTHLY':
            # Add one month (approximate)
            next_date = base_date + timedelta(days=30)
        else:
            return None
        
        # If the calculated next_date is in the past, find the next occurrence from today
        if next_date < today:
            # Find the next matching day from today
            days_ahead = (self.day_of_week - today.weekday()) % 7
            if days_ahead == 0:
                # If today is the right day, use today
                next_date = today
            else:
                next_date = today + timedelta(days=days_ahead)
        
        # Check if within end date range
        if self.end_date and next_date > self.end_date:
            return None
            
        return next_date


class StudentGroup(models.Model):
    """
    Groups of students that can be assigned to session templates.
    Advisors create and manage these groups.
    """
    
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    
    # Advisor who created/manages this group
    advisor = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='student_groups'
    )
    
    # Students in this group
    students = models.ManyToManyField(
        User, 
        related_name='assigned_groups',
        limit_choices_to={'role': 'student'}
    )
    
    # Status
    is_active = models.BooleanField(default=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
        indexes = [
            models.Index(fields=['advisor', 'is_active']),
            models.Index(fields=['name']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.students.count()} students)"
    
    @property
    def student_count(self):
        """Get number of students in group"""
        return self.students.count()
    
    def add_student(self, student):
        """Add a student to the group"""
        if student.role == 'student':
            self.students.add(student)
    
    def remove_student(self, student):
        """Remove a student from the group"""
        self.students.remove(student)


class TemplateGroupAssignment(models.Model):
    """
    Assignment of student groups to session templates.
    When a session is generated from a template, all students in assigned groups
    are automatically enrolled.
    """
    
    template = models.ForeignKey(
        SessionTemplate, 
        on_delete=models.CASCADE, 
        related_name='group_assignments'
    )
    group = models.ForeignKey(
        StudentGroup, 
        on_delete=models.CASCADE, 
        related_name='template_assignments'
    )
    advisor = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        related_name='template_group_assignments'
    )
    
    # Assignment Details
    assigned_date = models.DateTimeField(auto_now_add=True)
    assignment_message = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    
    # Tracking
    sessions_generated = models.IntegerField(default=0)
    last_session_date = models.DateField(null=True, blank=True)
    
    class Meta:
        unique_together = ('template', 'group')
        indexes = [
            models.Index(fields=['template', 'is_active']),
            models.Index(fields=['group', 'is_active']),
            models.Index(fields=['advisor', 'assigned_date']),
        ]
    
    def __str__(self):
        return f"{self.group.name} → {self.template.title}"
    
    def clean(self):
        """Validate assignment"""
        if self.template.teacher == self.advisor:
            raise ValidationError("Teachers cannot assign groups to their own templates")


class GeneratedSession(models.Model):
    """
    Tracking record for sessions generated from templates.
    Links LiveSession instances back to their source templates.
    """
    
    template = models.ForeignKey(
        SessionTemplate, 
        on_delete=models.CASCADE, 
        related_name='generated_sessions'
    )
    session = models.OneToOneField(
        LiveSession, 
        on_delete=models.CASCADE, 
        related_name='template_source'
    )
    
    # Generation Details
    generation_date = models.DateTimeField(auto_now_add=True)
    generated_by = models.CharField(
        max_length=50, 
        default='system',
        help_text="Who/what generated this session (system, manual, etc.)"
    )
    
    # Assignment Tracking
    students_assigned = models.IntegerField(default=0)
    groups_assigned = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['-generation_date']
        indexes = [
            models.Index(fields=['template', 'generation_date']),
            models.Index(fields=['session']),
        ]
    
    def __str__(self):
        return f"Generated: {self.session.title} from {self.template.title}"
    
    @property
    def is_upcoming(self):
        """Check if the generated session is upcoming"""
        return self.session.scheduled_datetime > timezone.now()
    
    @property
    def is_completed(self):
        """Check if the generated session is completed"""
        return self.session.status == 'COMPLETED'


class TemplateGenerationLog(models.Model):
    """
    Log of template generation attempts for debugging and monitoring.
    """
    
    STATUS_CHOICES = [
        ('SUCCESS', 'Success'),
        ('FAILED', 'Failed'),
        ('SKIPPED', 'Skipped'),
    ]
    
    template = models.ForeignKey(
        SessionTemplate, 
        on_delete=models.CASCADE, 
        related_name='generation_logs'
    )
    
    # Generation Details
    attempted_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    message = models.TextField(blank=True, null=True)
    
    # Results
    session_created = models.ForeignKey(
        LiveSession, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True
    )
    students_assigned = models.IntegerField(default=0)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['template', 'attempted_date']),
            models.Index(fields=['status', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.template.title} - {self.attempted_date} ({self.status})"