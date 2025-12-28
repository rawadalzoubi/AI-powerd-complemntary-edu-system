# backend/Education/Educational_system/eduAPI/urls/recurring_sessions_urls.py
# URLs for recurring sessions functionality

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from ..views.recurring_sessions_views import (
    SessionTemplateViewSet,
    StudentGroupViewSet,
    TemplateGroupAssignmentViewSet,
    GeneratedSessionViewSet,
    TemplateGenerationLogViewSet,
    get_available_students,
    get_my_recurring_sessions,
    get_template_statistics
)

# Create router for ViewSets
router = DefaultRouter()
router.register(r'templates', SessionTemplateViewSet, basename='sessiontemplate')
router.register(r'groups', StudentGroupViewSet, basename='studentgroup')
router.register(r'assignments', TemplateGroupAssignmentViewSet, basename='templategroupassignment')
router.register(r'generated-sessions', GeneratedSessionViewSet, basename='generatedsession')
router.register(r'generation-logs', TemplateGenerationLogViewSet, basename='templategenerationlog')

urlpatterns = [
    # ViewSet URLs
    path('', include(router.urls)),
    
    # Utility endpoints
    path('students/available/', get_available_students, name='available-students'),
    path('my-sessions/', get_my_recurring_sessions, name='my-recurring-sessions'),
    path('statistics/', get_template_statistics, name='template-statistics'),
]