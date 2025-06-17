from django.urls import path, include
from .views import serve_file
from .urls.user_urls import urlpatterns as user_urlpatterns
from .urls.lessons_urls import urlpatterns as lessons_urlpatterns

app_name = 'eduAPI'

urlpatterns = [
    path('user/', include(user_urlpatterns)),
    path('content/', include(lessons_urlpatterns)),
    
    # File serving endpoints - multiple paths for flexibility
    path('pdf-proxy/', serve_file, name='pdf-proxy'),
    path('file-serve/', serve_file, name='file-serve'),
    path('files/', serve_file, name='files'),  # Shorter alternative
    path('download/', serve_file, name='download'),  # Another option
]