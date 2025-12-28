from django.contrib import admin
from .models.user_model import User

# Import recurring sessions admin
from .admin.recurring_sessions_admin import *

# Very simple User admin - just register it
admin.site.register(User)

# Custom admin site configuration
admin.site.site_header = 'EduTrack Admin - Advisor Management'
admin.site.site_title = 'EduTrack Admin'
admin.site.index_title = 'Manage Advisors'
