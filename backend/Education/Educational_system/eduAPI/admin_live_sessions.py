# backend/Education/Educational_system/eduAPI/admin.py
# أضف هذا الكود للـ admin.py الموجود

from django.contrib import admin
from .models.live_sessions_models import (
    LiveSession,
    LiveSessionAssignment,
    LiveSessionMaterial,
    LiveSessionNote,
    LiveSessionNotification
)

@admin.register(LiveSession)
class LiveSessionAdmin(admin.ModelAdmin):
    list_display = ['title', 'teacher', 'subject', 'level', 'scheduled_datetime', 'status', 'assigned_students_count']
    list_filter = ['status', 'level', 'subject', 'created_at']
    search_fields = ['title', 'teacher__email', 'teacher__first_name', 'teacher__last_name']
    readonly_fields = ['jitsi_room_name', 'created_at', 'updated_at']
    date_hierarchy = 'scheduled_datetime'
    
    def assigned_students_count(self, obj):
        return obj.assignments.count()
    assigned_students_count.short_description = 'Students Assigned'

@admin.register(LiveSessionAssignment)
class LiveSessionAssignmentAdmin(admin.ModelAdmin):
    list_display = ['session', 'student', 'advisor', 'assigned_date', 'attended', 'attendance_percentage']
    list_filter = ['attended', 'assigned_date', 'session__status']
    search_fields = ['session__title', 'student__email', 'advisor__email']
    readonly_fields = ['assigned_date', 'attendance_percentage']

@admin.register(LiveSessionMaterial)
class LiveSessionMaterialAdmin(admin.ModelAdmin):
    list_display = ['title', 'session', 'content_type', 'uploaded_by', 'uploaded_at', 'is_public']
    list_filter = ['content_type', 'is_public', 'uploaded_at']
    search_fields = ['title', 'session__title', 'uploaded_by__email']
    readonly_fields = ['uploaded_at', 'file_size']

@admin.register(LiveSessionNote)
class LiveSessionNoteAdmin(admin.ModelAdmin):
    list_display = ['session', 'author', 'is_private', 'created_at']
    list_filter = ['is_private', 'created_at']
    search_fields = ['session__title', 'author__email', 'content']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(LiveSessionNotification)
class LiveSessionNotificationAdmin(admin.ModelAdmin):
    list_display = ['title', 'recipient', 'notification_type', 'is_read', 'created_at']
    list_filter = ['notification_type', 'is_read', 'created_at']
    search_fields = ['title', 'recipient__email', 'message']
    readonly_fields = ['created_at', 'read_at']