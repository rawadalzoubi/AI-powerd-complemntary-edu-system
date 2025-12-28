from django.urls import path
from ..views.advisor_management import (
    advisor_list,
    create_advisor,
    delete_advisor,
    reset_password,
    toggle_advisor_status,
    advisor_stats
)

urlpatterns = [
    path('', advisor_list, name='advisor_list'),
    path('create/', create_advisor, name='create_advisor'),
    path('delete/<int:advisor_id>/', delete_advisor, name='delete_advisor'),
    path('reset-password/<int:advisor_id>/', reset_password, name='reset_password'),
    path('toggle-status/<int:advisor_id>/', toggle_advisor_status, name='toggle_advisor_status'),
    path('stats/', advisor_stats, name='advisor_stats'),
]