# backend/Education/Educational_system/eduAPI/models/live_sessions_models.py
# Live Sessions Models - Following existing codebase patterns

from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
import uuid

User = get_user_model()

class LiveSession(models.Model):
    """
    Live session model for real-time classes.
    Similar to Lesson model but for live interactive sessions.
    """
    
    STATUS_CHOICES = [
        ('PENDING', 'Pending Assignment'),
        ('ASSIGNED', 'Assigned to Students'),
        ('ACTIVE', 'Currently Active'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled')
    ]
    
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
    
    # Basic Information
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    subject = models.CharField(max_length=255)
    level = models.CharField(max_length=2, choices=GRADE_CHOICES)
    
    # Relationships - following existing pattern
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, related_name='live_sessions')
    
    # Scheduling
    scheduled_datetime = models.DateTimeField()
    duration_minutes = models.IntegerField(
        default=60,
        validators=[MinValueValidator(15), MaxValueValidator(240)]
    )
    
    # Jitsi Integration
    jitsi_room_name = models.CharField(max_length=100, unique=True)
    jitsi_room_password = models.CharField(max_length=50, blank=True, null=True)
    
    # Status and Metadata
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    max_participants = models.IntegerField(default=50)
    
    # Timestamps - following existing pattern
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Tracking
    actual_start_time = models.DateTimeField(null=True, blank=True)
    actual_end_time = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-scheduled_datetime']
        indexes = [
            models.Index(fields=['teacher', 'status']),
            models.Index(fields=['scheduled_datetime']),
            models.Index(fields=['status', 'scheduled_datetime']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.subject} (Grade {self.level})"
    
    @property
    def is_active(self):
        """Check if session is currently active"""
        if self.status != 'ASSIGNED':
            return False
        now = timezone.now()
        session_start = self.scheduled_datetime
        session_end = session_start + timezone.timedelta(minutes=self.duration_minutes)
        return session_start <= now <= session_end
    
    @property
    def can_be_modified(self):
        """Check if session can be modified"""
        return self.status in ['PENDING', 'ASSIGNED'] and not self.is_active


class LiveSessionAssignment(models.Model):
    """
    Assignment of live sessions to students by advisors.
    Similar to LessonAssignment model pattern.
    """
    
    session = models.ForeignKey(LiveSession, on_delete=models.CASCADE, related_name='assignments')
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='assigned_live_sessions')
    advisor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='live_session_assignments')
    
    # Assignment Details
    assigned_date = models.DateTimeField(auto_now_add=True)
    assignment_message = models.TextField(blank=True, null=True)
    
    # Attendance Tracking - following existing pattern
    attended = models.BooleanField(default=False)
    join_time = models.DateTimeField(null=True, blank=True)
    leave_time = models.DateTimeField(null=True, blank=True)
    attendance_duration_minutes = models.IntegerField(default=0)
    
    class Meta:
        unique_together = ('session', 'student')
        indexes = [
            models.Index(fields=['student', 'session']),
            models.Index(fields=['advisor', 'assigned_date']),
        ]
    
    def __str__(self):
        return f"{self.session.title} assigned to {self.student.first_name} {self.student.last_name}"
    
    @property
    def attendance_percentage(self):
        """Calculate attendance percentage"""
        if self.attendance_duration_minutes == 0:
            return 0
        return min(100, (self.attendance_duration_minutes / self.session.duration_minutes) * 100)
    
    def save(self, *args, **kwargs):
        """Override save to update session status - following existing pattern"""
        super().save(*args, **kwargs)
        
        # Update session status to ASSIGNED if it was PENDING
        if self.session.status == 'PENDING':
            self.session.status = 'ASSIGNED'
            self.session.save()


class LiveSessionMaterial(models.Model):
    """
    Materials for live sessions.
    Following LessonContent model pattern.
    """
    
    TYPE_CHOICES = [
        ('PDF', 'PDF Document'),
        ('PPT', 'Presentation'),
        ('DOC', 'Document'),
        ('VIDEO', 'Video Content'),
        ('AUDIO', 'Audio Content'),
        ('IMAGE', 'Image Content'),
        ('LINK', 'External Link'),
        ('OTHER', 'Other Content Type')
    ]
    
    session = models.ForeignKey(LiveSession, on_delete=models.CASCADE, related_name='materials')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    content_type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    
    # File handling - following existing pattern
    file = models.FileField(upload_to='live_session_materials/', blank=True, null=True)
    url = models.URLField(blank=True, null=True)
    text_content = models.TextField(blank=True, null=True)
    
    # Metadata
    file_size = models.BigIntegerField(null=True, blank=True)  # in bytes
    order = models.IntegerField(default=0)
    
    # Relationships
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Access Control
    is_public = models.BooleanField(default=True)  # Available to all assigned students
    
    class Meta:
        ordering = ['order', 'created_at']
        indexes = [
            models.Index(fields=['session', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.title} ({self.get_content_type_display()})"


class LiveSessionNote(models.Model):
    """
    Notes and feedback for live sessions.
    Similar to StudentFeedback pattern.
    """
    
    session = models.ForeignKey(LiveSession, on_delete=models.CASCADE, related_name='notes')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    is_private = models.BooleanField(default=False)  # Private to teacher/advisor
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['session', 'created_at']),
        ]
    
    def __str__(self):
        return f"Note for {self.session.title} by {self.author.get_full_name()}"


class LiveSessionNotification(models.Model):
    """
    Notifications for live sessions.
    Following existing notification patterns.
    """
    
    NOTIFICATION_TYPES = [
        ('SESSION_ASSIGNED', 'Session Assigned'),
        ('SESSION_REMINDER', 'Session Reminder'),
        ('SESSION_CANCELLED', 'Session Cancelled'),
        ('SESSION_UPDATED', 'Session Updated'),
        ('MATERIAL_UPLOADED', 'Material Uploaded'),
        ('ATTENDANCE_ALERT', 'Attendance Alert'),
    ]
    
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='live_session_notifications')
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=255)
    message = models.TextField()
    
    # Related Objects
    session = models.ForeignKey(LiveSession, on_delete=models.CASCADE, null=True, blank=True)
    
    # Status - following existing pattern
    is_read = models.BooleanField(default=False)
    is_sent_email = models.BooleanField(default=False)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['recipient', 'is_read', 'created_at']),
            models.Index(fields=['notification_type', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.recipient.get_full_name()}"