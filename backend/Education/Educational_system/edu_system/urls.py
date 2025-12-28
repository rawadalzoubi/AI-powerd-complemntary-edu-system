"""
Root URL configuration for edu_system project.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from eduAPI.models import Lesson, StudentEnrollment
from eduAPI.views.media_views import serve_file, direct_download
from eduAPI.views.admin_views import reset_advisor_password, advisor_stats
from eduAPI.views.simple_live_sessions import (
    test_live_sessions,
    test_live_sessions_no_auth,
    get_sessions, 
    get_my_schedule, 
    get_pending_sessions,
    join_session,
    assign_session,
    unassign_session,
    get_assigned_students,
    update_session,
    cancel_session,
    debug_sessions
)

# EMERGENCY DEBUG VIEW
@api_view(['GET'])
def emergency_lesson_35(request):
    """Emergency direct access to lesson 35 data"""
    try:
        # Try to get lesson 35
        try:
            lesson = Lesson.objects.get(id=35)
            print(f"DEBUG: Found lesson 35: {lesson.name}")
        except:
            print("DEBUG: Lesson 35 not found!")
            return JsonResponse({"detail": "Lesson 35 not found in database"}, status=404)
            
        # Return basic lesson data
        data = {
            "id": lesson.id,
            "name": lesson.name,
            "description": lesson.description,
            "subject": lesson.subject,
            "level": lesson.level,
            "progress": 0,
            "status": "Available"
        }
        
        print(f"DEBUG: Returning lesson data: {data}")
        return JsonResponse(data)
        
    except Exception as e:
        print(f"DEBUG ERROR: {str(e)}")
        return JsonResponse({"detail": f"Error: {str(e)}"}, status=500)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),  # Login/logout URLs
    path('advisors/', include('eduAPI.urls.advisor_urls')),  # Advisor Management Interface
    path('admin/reset-advisor-password/<int:user_id>/', reset_advisor_password, name='reset_advisor_password'),
    path('admin/advisor-stats/', advisor_stats, name='advisor_stats'),
    path('api/', include('eduAPI.urls')),
    path('debug/lesson35/', emergency_lesson_35, name='emergency_lesson_35'),  # EMERGENCY DEBUG ENDPOINT
    
    # Direct recurring sessions URLs - temporary fix
    path('api/recurring-sessions/', include('eduAPI.urls.recurring_sessions_urls')),
    
    # Live Sessions URLs - Direct import
    path('api/live-sessions/test/', test_live_sessions, name='live-sessions-test'),
    path('api/live-sessions/test-no-auth/', test_live_sessions_no_auth, name='live-sessions-test-no-auth'),
    path('api/live-sessions/debug/', debug_sessions, name='debug-sessions'),
    path('api/live-sessions/', get_sessions, name='live-sessions-list'),
    path('api/live-sessions/my-schedule/', get_my_schedule, name='my-schedule'),
    path('api/live-sessions/pending/', get_pending_sessions, name='pending-sessions'),
    path('api/live-sessions/<str:session_id>/', update_session, name='update-session'),
    path('api/live-sessions/<str:session_id>/assign/', assign_session, name='assign-session'),
    path('api/live-sessions/<str:session_id>/unassign/', unassign_session, name='unassign-session'),
    path('api/live-sessions/<str:session_id>/assigned-students/', get_assigned_students, name='get-assigned-students'),
    path('api/live-sessions/<str:session_id>/cancel/', cancel_session, name='cancel-session'),
    path('api/live-sessions/<str:session_id>/join/', join_session, name='join-session'),
    
    # Direct file download endpoints
    path('api/file-serve/', serve_file, name='file-serve-direct'),
    path('api/files/', serve_file, name='files-direct'),
    path('api/download/', serve_file, name='download-direct'),
    
    # Direct download by filename (more flexible approach)
    path('download/<str:filename>', direct_download, name='direct-download'),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
