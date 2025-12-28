# backend/Education/Educational_system/eduAPI/serializers/recurring_sessions_serializers.py
# Serializers for recurring sessions functionality

from rest_framework import serializers
from django.contrib.auth import get_user_model
from ..models.recurring_sessions_models import (
    SessionTemplate, 
    StudentGroup, 
    TemplateGroupAssignment, 
    GeneratedSession,
    TemplateGenerationLog
)
from ..models.live_sessions_models import LiveSession

User = get_user_model()


class SessionTemplateSerializer(serializers.ModelSerializer):
    """Serializer for SessionTemplate model"""
    
    teacher_name = serializers.CharField(source='teacher.get_full_name', read_only=True)
    day_of_week_display = serializers.CharField(source='get_day_of_week_display', read_only=True)
    recurrence_type_display = serializers.CharField(source='get_recurrence_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    next_generation_date = serializers.DateField(read_only=True)
    assigned_groups_count = serializers.SerializerMethodField()
    
    class Meta:
        model = SessionTemplate
        fields = [
            'id', 'title', 'description', 'subject', 'level',
            'teacher', 'teacher_name',
            'day_of_week', 'day_of_week_display',
            'start_time', 'duration_minutes',
            'recurrence_type', 'recurrence_type_display',
            'start_date', 'end_date',
            'status', 'status_display',
            'max_participants',
            'last_generated', 'total_generated',
            'next_generation_date', 'assigned_groups_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['teacher', 'last_generated', 'total_generated', 'created_at', 'updated_at']
    
    def get_assigned_groups_count(self, obj):
        """Get count of assigned groups"""
        return obj.group_assignments.filter(is_active=True).count()
    
    def validate(self, data):
        """Validate template data"""
        if data.get('end_date') and data.get('start_date'):
            if data['end_date'] <= data['start_date']:
                raise serializers.ValidationError("End date must be after start date")
        return data
    
    def create(self, validated_data):
        """Create template with current user as teacher"""
        validated_data['teacher'] = self.context['request'].user
        return super().create(validated_data)


class StudentGroupSerializer(serializers.ModelSerializer):
    """Serializer for StudentGroup model"""
    
    advisor_name = serializers.CharField(source='advisor.get_full_name', read_only=True)
    student_count = serializers.IntegerField(read_only=True)
    students_details = serializers.SerializerMethodField(read_only=True)
    template_assignments_count = serializers.SerializerMethodField()
    
    class Meta:
        model = StudentGroup
        fields = [
            'id', 'name', 'description',
            'advisor', 'advisor_name',
            'students', 'students_details', 'student_count',
            'template_assignments_count',
            'is_active',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['advisor', 'created_at', 'updated_at']
    
    def get_students_details(self, obj):
        """Get detailed student information"""
        return [
            {
                'id': student.id,
                'first_name': student.first_name,
                'last_name': student.last_name,
                'email': student.email,
                'full_name': student.get_full_name()
            }
            for student in obj.students.all()
        ]
    
    def get_template_assignments_count(self, obj):
        """Get count of template assignments"""
        return obj.template_assignments.filter(is_active=True).count()
    
    def create(self, validated_data):
        """Create group with current user as advisor"""
        students_data = validated_data.pop('students', [])
        validated_data['advisor'] = self.context['request'].user
        group = super().create(validated_data)
        
        # Add students to group
        for student in students_data:
            if student.role == 'student':
                group.students.add(student)
        
        return group
    
    def update(self, instance, validated_data):
        """Update group and handle student assignments"""
        students_data = validated_data.pop('students', None)
        instance = super().update(instance, validated_data)
        
        if students_data is not None:
            # Clear existing students and add new ones
            instance.students.clear()
            for student in students_data:
                if student.role == 'student':
                    instance.students.add(student)
        
        return instance


class TemplateGroupAssignmentSerializer(serializers.ModelSerializer):
    """Serializer for TemplateGroupAssignment model"""
    
    template_title = serializers.CharField(source='template.title', read_only=True)
    group_name = serializers.CharField(source='group.name', read_only=True)
    advisor_name = serializers.CharField(source='advisor.get_full_name', read_only=True)
    student_count = serializers.CharField(source='group.student_count', read_only=True)
    
    class Meta:
        model = TemplateGroupAssignment
        fields = [
            'id', 'template', 'template_title',
            'group', 'group_name', 'student_count',
            'advisor', 'advisor_name',
            'assigned_date', 'assignment_message',
            'is_active',
            'sessions_generated', 'last_session_date'
        ]
        read_only_fields = ['advisor', 'assigned_date', 'sessions_generated', 'last_session_date']
    
    def create(self, validated_data):
        """Create assignment with current user as advisor"""
        validated_data['advisor'] = self.context['request'].user
        return super().create(validated_data)
    
    def validate(self, data):
        """Validate assignment"""
        template = data.get('template')
        group = data.get('group')
        
        if template and group:
            # Check if assignment already exists
            if TemplateGroupAssignment.objects.filter(
                template=template, 
                group=group, 
                is_active=True
            ).exists():
                raise serializers.ValidationError("This group is already assigned to this template")
            
            # Check if advisor owns the group
            request_user = self.context['request'].user
            if group.advisor != request_user:
                raise serializers.ValidationError("You can only assign your own groups")
        
        return data


class GeneratedSessionSerializer(serializers.ModelSerializer):
    """Serializer for GeneratedSession model"""
    
    template_title = serializers.CharField(source='template.title', read_only=True)
    session_details = serializers.SerializerMethodField()
    
    class Meta:
        model = GeneratedSession
        fields = [
            'id', 'template', 'template_title',
            'session', 'session_details',
            'generation_date', 'generated_by',
            'students_assigned', 'groups_assigned'
        ]
        read_only_fields = ['generation_date']
    
    def get_session_details(self, obj):
        """Get session details"""
        session = obj.session
        return {
            'id': session.id,
            'title': session.title,
            'scheduled_datetime': session.scheduled_datetime,
            'status': session.status,
            'duration_minutes': session.duration_minutes,
            'assigned_students_count': session.assignments.count()
        }


class TemplateGenerationLogSerializer(serializers.ModelSerializer):
    """Serializer for TemplateGenerationLog model"""
    
    template_title = serializers.CharField(source='template.title', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = TemplateGenerationLog
        fields = [
            'id', 'template', 'template_title',
            'attempted_date', 'status', 'status_display',
            'message', 'session_created', 'students_assigned',
            'created_at'
        ]
        read_only_fields = ['created_at']


# Simplified serializers for dropdowns and selections
class SessionTemplateSimpleSerializer(serializers.ModelSerializer):
    """Simple serializer for template selection"""
    
    teacher_name = serializers.CharField(source='teacher.get_full_name', read_only=True)
    schedule_display = serializers.SerializerMethodField()
    
    class Meta:
        model = SessionTemplate
        fields = ['id', 'title', 'teacher_name', 'schedule_display', 'status']
    
    def get_schedule_display(self, obj):
        """Get readable schedule display"""
        return f"{obj.get_day_of_week_display()} at {obj.start_time.strftime('%H:%M')}"


class StudentGroupSimpleSerializer(serializers.ModelSerializer):
    """Simple serializer for group selection"""
    
    student_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = StudentGroup
        fields = ['id', 'name', 'student_count', 'is_active']


class StudentSimpleSerializer(serializers.ModelSerializer):
    """Simple serializer for student selection"""
    
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'full_name', 'email']