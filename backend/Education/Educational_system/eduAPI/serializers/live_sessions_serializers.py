# backend/Education/Educational_system/eduAPI/serzers.pyserialiessions_s/live_szeriali
# Live Sessions Serializers - Following existing codebase patterns

from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta

from ..models.live_sessions_models import (
    LiveSession,
    LiveSessionAssignment,
    LiveSessionMaterial,
    LiveSessionNote,
    LiveSessionNotification
)

User = get_user_model()


class UserBasicSerializer(serializers.ModelSerializer):
    """Basic user serializer for nested relationships"""
    
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'full_name', 'role']
        read_only_fields = ['id', 'email', 'role']


class LiveSessionSerializer(serializers.ModelSerializer):
    """
    Basic live session serializer.
    Following existing serializer patterns in the codebase.
    """
    
    teacher = UserBasicSerializer(read_only=True)
    teacher_name = serializers.CharField(source='teacher.get_full_name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    level_display = serializers.CharField(source='get_level_display', read_only=True)
    
    # Computed fields
    is_active = serializers.BooleanField(read_only=True)
    can_be_modified = serializers.BooleanField(read_only=True)
    assigned_students_count = serializers.SerializerMethodField()
    
    class Meta:
        model = LiveSession
        fields = [
            'id', 'title', 'description', 'subject', 'level', 'level_display',
            'teacher', 'teacher_name', 'scheduled_datetime', 'duration_minutes',
            'status', 'status_display', 'max_participants',
            'created_at', 'updated_at', 'is_active', 'can_be_modified',
            'assigned_students_count'
        ]
        read_only_fields = [
            'id', 'teacher', 'teacher_name', 'status', 'status_display',
            'created_at', 'updated_at', 'is_active', 'can_be_modified',
            'assigned_students_count'
        ]
    
    def get_assigned_students_count(self, obj):
        """Get count of assigned students"""
        return obj.assignments.count()
    
    def validate_scheduled_datetime(self, value):
        """Validate that session is scheduled in the future"""
        if value <= timezone.now():
            raise serializers.ValidationError(
                "Session must be scheduled in the future"
            )
        return value
    
    def validate(self, data):
        """Additional validation"""
        # Check for teacher scheduling conflicts
        if self.instance is None:  # Creating new session
            teacher = self.context['request'].user
            scheduled_datetime = data.get('scheduled_datetime')
            duration_minutes = data.get('duration_minutes', 60)
            
            if scheduled_datetime:
                # Check for overlapping sessions
                session_end = scheduled_datetime + timedelta(minutes=duration_minutes)
                
                overlapping_sessions = LiveSession.objects.filter(
                    teacher=teacher,
                    status__in=['PENDING', 'ASSIGNED', 'ACTIVE'],
                    scheduled_datetime__lt=session_end,
                    scheduled_datetime__gte=scheduled_datetime - timedelta(minutes=240)  # Max session duration
                ).exclude(pk=self.instance.pk if self.instance else None)
                
                if overlapping_sessions.exists():
                    raise serializers.ValidationError(
                        "You have another session scheduled at this time"
                    )
        
        return data


class LiveSessionMaterialSerializer(serializers.ModelSerializer):
    """
    Serializer for session materials.
    Following existing material serializer patterns.
    """
    
    uploaded_by = UserBasicSerializer(read_only=True)
    uploaded_by_name = serializers.CharField(source='uploaded_by.get_full_name', read_only=True)
    content_type_display = serializers.CharField(source='get_content_type_display', read_only=True)
    file_size_mb = serializers.SerializerMethodField()
    
    class Meta:
        model = LiveSessionMaterial
        fields = [
            'id', 'title', 'description', 'content_type', 'content_type_display',
            'file', 'url', 'text_content', 'file_size', 'file_size_mb',
            'order', 'uploaded_by', 'uploaded_by_name', 'is_public',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'uploaded_by', 'uploaded_by_name', 'file_size', 'file_size_mb',
            'created_at', 'updated_at'
        ]
    
    def get_file_size_mb(self, obj):
        """Convert file size to MB"""
        if obj.file_size:
            return round(obj.file_size / (1024 * 1024), 2)
        return None
    
    def validate(self, data):
        """Validate material data"""
        content_type = data.get('content_type')
        file = data.get('file')
        url = data.get('url')
        text_content = data.get('text_content')
        
        # Ensure at least one content source is provided
        if not any([file, url, text_content]):
            raise serializers.ValidationError(
                "At least one of file, URL, or text content must be provided"
            )
        
        # Validate file size (max 100MB)
        if file and file.size > 100 * 1024 * 1024:
            raise serializers.ValidationError(
                "File size cannot exceed 100MB"
            )
        
        return data


class SessionAssignmentSerializer(serializers.ModelSerializer):
    """
    Serializer for session assignments.
    Following existing assignment serializer patterns.
    """
    
    session = LiveSessionSerializer(read_only=True)
    student = UserBasicSerializer(read_only=True)
    advisor = UserBasicSerializer(read_only=True)
    
    student_name = serializers.CharField(source='student.get_full_name', read_only=True)
    advisor_name = serializers.CharField(source='advisor.get_full_name', read_only=True)
    session_title = serializers.CharField(source='session.title', read_only=True)
    
    attendance_percentage = serializers.ReadOnlyField()
    
    class Meta:
        model = LiveSessionAssignment
        fields = [
            'id', 'session', 'session_title', 'student', 'student_name',
            'advisor', 'advisor_name', 'assigned_date', 'assignment_message',
            'attended', 'join_time', 'leave_time', 'attendance_duration_minutes',
            'attendance_percentage'
        ]
        read_only_fields = [
            'id', 'session', 'session_title', 'student', 'student_name',
            'advisor', 'advisor_name', 'assigned_date', 'attended',
            'join_time', 'leave_time', 'attendance_duration_minutes',
            'attendance_percentage'
        ]


class LiveSessionNoteSerializer(serializers.ModelSerializer):
    """
    Serializer for session notes.
    Following existing note/feedback serializer patterns.
    """
    
    author = UserBasicSerializer(read_only=True)
    author_name = serializers.CharField(source='author.get_full_name', read_only=True)
    
    class Meta:
        model = LiveSessionNote
        fields = [
            'id', 'content', 'is_private', 'author', 'author_name',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'author', 'author_name', 'created_at', 'updated_at']


class LiveSessionDetailSerializer(LiveSessionSerializer):
    """
    Detailed session serializer with related data.
    Following existing detail serializer patterns.
    """
    
    assignments = SessionAssignmentSerializer(many=True, read_only=True)
    materials = LiveSessionMaterialSerializer(many=True, read_only=True)
    notes = serializers.SerializerMethodField()
    
    # Additional computed fields
    total_assigned_students = serializers.SerializerMethodField()
    attended_students = serializers.SerializerMethodField()
    attendance_rate = serializers.SerializerMethodField()
    
    class Meta(LiveSessionSerializer.Meta):
        fields = LiveSessionSerializer.Meta.fields + [
            'assignments', 'materials', 'notes',
            'total_assigned_students', 'attended_students', 'attendance_rate',
            'jitsi_room_name', 'actual_start_time', 'actual_end_time'
        ]
        read_only_fields = LiveSessionSerializer.Meta.read_only_fields + [
            'assignments', 'materials', 'notes',
            'total_assigned_students', 'attended_students', 'attendance_rate',
            'jitsi_room_name', 'actual_start_time', 'actual_end_time'
        ]
    
    def get_notes(self, obj):
        """Get notes based on user permissions"""
        user = self.context['request'].user
        notes = obj.notes.all()
        
        # Filter private notes
        if user.role == 'student':
            notes = notes.filter(is_private=False)
        
        return LiveSessionNoteSerializer(notes, many=True).data
    
    def get_total_assigned_students(self, obj):
        """Get total number of assigned students"""
        return obj.assignments.count()
    
    def get_attended_students(self, obj):
        """Get number of students who attended"""
        return obj.assignments.filter(attended=True).count()
    
    def get_attendance_rate(self, obj):
        """Calculate attendance rate"""
        total = obj.assignments.count()
        if total == 0:
            return 0
        attended = obj.assignments.filter(attended=True).count()
        return round((attended / total) * 100, 2)


class LiveSessionNotificationSerializer(serializers.ModelSerializer):
    """
    Serializer for session notifications.
    Following existing notification serializer patterns.
    """
    
    recipient = UserBasicSerializer(read_only=True)
    session = LiveSessionSerializer(read_only=True)
    notification_type_display = serializers.CharField(source='get_notification_type_display', read_only=True)
    
    class Meta:
        model = LiveSessionNotification
        fields = [
            'id', 'recipient', 'notification_type', 'notification_type_display',
            'title', 'message', 'session', 'is_read', 'is_sent_email',
            'created_at', 'read_at'
        ]
        read_only_fields = [
            'id', 'recipient', 'notification_type_display', 'session',
            'is_sent_email', 'created_at', 'read_at'
        ]


class SessionCreateSerializer(serializers.ModelSerializer):
    """
    Simplified serializer for session creation.
    Following existing create serializer patterns.
    """
    
    class Meta:
        model = LiveSession
        fields = [
            'title', 'description', 'subject', 'level',
            'scheduled_datetime', 'duration_minutes', 'max_participants'
        ]
    
    def validate_scheduled_datetime(self, value):
        """Validate that session is scheduled in the future"""
        if value <= timezone.now():
            raise serializers.ValidationError(
                "Session must be scheduled in the future"
            )
        return value


class SessionAssignmentCreateSerializer(serializers.Serializer):
    """
    Serializer for creating session assignments.
    Following existing assignment creation patterns.
    """
    
    student_ids = serializers.ListField(
        child=serializers.UUIDField(),
        min_length=1,
        help_text="List of student IDs to assign the session to"
    )
    assignment_message = serializers.CharField(
        max_length=500,
        required=False,
        allow_blank=True,
        help_text="Optional message to include with the assignment"
    )
    
    def validate_student_ids(self, value):
        """Validate that all provided IDs are valid students"""
        students = User.objects.filter(
            id__in=value,
            role='student'
        )
        
        if len(students) != len(value):
            raise serializers.ValidationError(
                "One or more invalid student IDs provided"
            )
        
        return value


class CalendarSessionSerializer(serializers.ModelSerializer):
    """
    Simplified serializer for calendar view.
    Following existing calendar serializer patterns.
    """
    
    teacher_name = serializers.CharField(source='teacher.get_full_name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    level_display = serializers.CharField(source='get_level_display', read_only=True)
    
    # Calendar-specific fields
    start = serializers.DateTimeField(source='scheduled_datetime', read_only=True)
    end = serializers.SerializerMethodField()
    can_join = serializers.SerializerMethodField()
    
    class Meta:
        model = LiveSession
        fields = [
            'id', 'title', 'subject', 'level', 'level_display',
            'teacher_name', 'status', 'status_display',
            'start', 'end', 'duration_minutes', 'can_join'
        ]
    
    def get_end(self, obj):
        """Calculate session end time"""
        return obj.scheduled_datetime + timedelta(minutes=obj.duration_minutes)
    
    def get_can_join(self, obj):
        """Check if current user can join this session"""
        user = self.context['request'].user
        
        if user.role == 'teacher' and user == obj.teacher:
            return obj.is_active
        elif user.role == 'student':
            return (obj.is_active and 
                   obj.assignments.filter(student=user).exists())
        
        return False