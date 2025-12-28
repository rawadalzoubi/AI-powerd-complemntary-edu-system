from django.urls import path, include
from django.http import JsonResponse
from .models.recurring_sessions_models import SessionTemplate

def test_recurring_sessions(request):
    return JsonResponse({"message": "Recurring sessions endpoint is working!", "status": "success"})

def debug_templates(request):
    """Debug endpoint to check templates"""
    templates = SessionTemplate.objects.all()
    data = []
    for t in templates:
        data.append({
            "id": t.id,
            "title": t.title,
            "teacher": t.teacher.email,
            "subject": t.subject,
            "level": t.level
        })
    return JsonResponse({"templates": data, "count": len(data)})

app_name = 'eduAPI'

urlpatterns = [
    path('recurring-sessions/test/', test_recurring_sessions, name='test-recurring-sessions'),
    path('recurring-sessions/debug/', debug_templates, name='debug-templates'),
]