from django.urls import path
from django.http import JsonResponse

def test_view(request):
    return JsonResponse({"message": "Test working!"})

urlpatterns = [
    path('test/', test_view, name='test'),
]