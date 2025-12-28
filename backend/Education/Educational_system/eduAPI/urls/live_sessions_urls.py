from django.urls import path
from ..views.simple_live_sessions import (
    test_live_sessions, 
    get_sessions, 
    get_my_schedule, 
    get_pending_sessions,
    join_session
)

urlpatterns = [
    path('test/', test_live_sessions, name='live-sessions-test'),
    path('', get_sessions, name='live-sessions-list'),
    path('my-schedule/', get_my_schedule, name='my-schedule'),
    path('pending/', get_pending_sessions, name='pending-sessions'),
    path('<str:session_id>/join/', join_session, name='join-session'),
]