# Import user_urls directly, don't import specific views
from .user_urls import urlpatterns as user_urls
from .lessons_urls import urlpatterns as lessons_urls
from .student_urls import urlpatterns as student_urls
from django.urls import path, include

urlpatterns = [
    path('user/', include(user_urls)),
    path('content/', include(lessons_urls)),
    path('student/', include(student_urls)),
]

