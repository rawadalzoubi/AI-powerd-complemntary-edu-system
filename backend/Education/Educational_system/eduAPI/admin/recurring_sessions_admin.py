# backend/Education/Educational_system/eduAPI/admin/recurring_sessions_admin.py
# Admin interface for recurring sessions models

from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from ..models.recurring_sessions_models import (
    SessionTemplate,
    StudentGroup,
    TemplateGroupAssignment,
    GeneratedSession,
    TemplateGenerationLog
)


@admin.register(SessionTemplate)
class SessionTemplateAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'teacher', 'subject', 'level', 'day_of_week', 
        'start_time', 'recurrence_type', 'status', 'total_generated',
        'next_generation_date', 'created_at'
    ]
    list_filter = [
        'status', 'recurrence_type', 'day_of_week', 'subject', 
        'level', 'created_at'
    ]
    search_fields = ['title', 'teacher__email', 'teacher__first_name', 'teacher__last_name']
    readonly_fields = ['total_generated', 'last_generated', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'teacher', 'subject', 'level')
        }),
        ('Schedule', {
            'fields': ('day_of_week', 'start_time', 'duration_minutes', 'max_participants')
        }),
        ('Recurrence', {
            'fields': ('recurrence_type', 'start_date', 'end_date', 'status')
        }),
        ('Tracking', {
            'fields': ('total_generated', 'last_generated'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('teacher')
    
    def next_generation_date(self, obj):
        next_date = obj.next_generation_date
        if next_date:
            return next_date.strftime('%Y-%m-%d')
        return '-'
    next_generation_date.short_description = 'Next Generation'
    
    actions = ['pause_templates', 'resume_templates', 'end_templates']
    
    def pause_templates(self, request, queryset):
        updated = queryset.update(status='PAUSED')
        self.message_user(request, f'{updated} templates paused.')
    pause_templates.short_description = 'Pause selected templates'
    
    def resume_templates(self, request, queryset):
        updated = queryset.update(status='ACTIVE')
        self.message_user(request, f'{updated} templates resumed.')
    resume_templates.short_description = 'Resume selected templates'
    
    def end_templates(self, request, queryset):
        updated = queryset.update(status='ENDED')
        self.message_user(request, f'{updated} templates ended.')
    end_templates.short_description = 'End selected templates'


@admin.register(StudentGroup)
class StudentGroupAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'advisor', 'student_count', 'is_active', 
        'template_assignments_count', 'created_at'
    ]
    list_filter = ['is_active', 'created_at', 'advisor']
    search_fields = ['name', 'advisor__email', 'advisor__first_name', 'advisor__last_name']
    filter_horizontal = ['students']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'advisor', 'is_active')
        }),
        ('Students', {
            'fields': ('students',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('advisor').prefetch_related('students')
    
    def student_count(self, obj):
        return obj.student_count
    student_count.short_description = 'Students'
    
    def template_assignments_count(self, obj):
        count = obj.template_assignments.filter(is_active=True).count()
        if count > 0:
            return format_html(
                '<a href="{}?group__id__exact={}">{} assignments</a>',
                reverse('admin:eduAPI_templategroupassignment_changelist'),
                obj.id,
                count
            )
        return '0 assignments'
    template_assignments_count.short_description = 'Template Assignments'


@admin.register(TemplateGroupAssignment)
class TemplateGroupAssignmentAdmin(admin.ModelAdmin):
    list_display = [
        'template', 'group', 'advisor', 'is_active', 
        'sessions_generated', 'last_session_date', 'assigned_date'
    ]
    list_filter = ['is_active', 'assigned_date', 'advisor']
    search_fields = [
        'template__title', 'group__name', 'advisor__email',
        'advisor__first_name', 'advisor__last_name'
    ]
    readonly_fields = ['sessions_generated', 'last_session_date', 'assigned_date']
    
    fieldsets = (
        ('Assignment', {
            'fields': ('template', 'group', 'advisor', 'is_active')
        }),
        ('Details', {
            'fields': ('assignment_message',)
        }),
        ('Tracking', {
            'fields': ('sessions_generated', 'last_session_date', 'assigned_date'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'template', 'group', 'advisor'
        )


@admin.register(GeneratedSession)
class GeneratedSessionAdmin(admin.ModelAdmin):
    list_display = [
        'session_title', 'template', 'session_date', 'students_assigned',
        'groups_assigned', 'generation_date', 'session_status'
    ]
    list_filter = ['generation_date', 'generated_by', 'template__subject']
    search_fields = [
        'session__title', 'template__title', 'template__teacher__email'
    ]
    readonly_fields = [
        'generation_date', 'students_assigned', 'groups_assigned'
    ]
    
    fieldsets = (
        ('Generated Session', {
            'fields': ('template', 'session', 'generated_by')
        }),
        ('Assignment Details', {
            'fields': ('students_assigned', 'groups_assigned')
        }),
        ('Timestamps', {
            'fields': ('generation_date',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'template', 'session', 'template__teacher'
        )
    
    def session_title(self, obj):
        return obj.session.title
    session_title.short_description = 'Session Title'
    
    def session_date(self, obj):
        return obj.session.scheduled_datetime.strftime('%Y-%m-%d %H:%M')
    session_date.short_description = 'Session Date'
    
    def session_status(self, obj):
        status = obj.session.status
        colors = {
            'PENDING': 'orange',
            'ASSIGNED': 'blue',
            'ACTIVE': 'green',
            'COMPLETED': 'gray',
            'CANCELLED': 'red'
        }
        color = colors.get(status, 'black')
        return format_html(
            '<span style="color: {};">{}</span>',
            color,
            status
        )
    session_status.short_description = 'Status'


@admin.register(TemplateGenerationLog)
class TemplateGenerationLogAdmin(admin.ModelAdmin):
    list_display = [
        'template', 'attempted_date', 'status', 'students_assigned',
        'session_created_link', 'created_at'
    ]
    list_filter = ['status', 'attempted_date', 'created_at']
    search_fields = ['template__title', 'message']
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('Generation Attempt', {
            'fields': ('template', 'attempted_date', 'status')
        }),
        ('Results', {
            'fields': ('session_created', 'students_assigned', 'message')
        }),
        ('Timestamps', {
            'fields': ('created_at',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'template', 'session_created'
        )
    
    def session_created_link(self, obj):
        if obj.session_created:
            return format_html(
                '<a href="{}">View Session</a>',
                reverse('admin:eduAPI_livesession_change', args=[obj.session_created.id])
            )
        return '-'
    session_created_link.short_description = 'Session Created'
    
    def has_add_permission(self, request):
        # Logs are created automatically, don't allow manual creation
        return False
    
    def has_change_permission(self, request, obj=None):
        # Logs should be read-only
        return False