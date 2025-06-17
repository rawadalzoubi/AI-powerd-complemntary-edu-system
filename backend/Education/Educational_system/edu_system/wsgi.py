"""
WSGI config for edu_system project.

Exposes the WSGI callable as a module-level variable named ``application``.
"""

import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'edu_system.settings')

application = get_wsgi_application() 