import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'edu_system.settings')
django.setup()

from eduAPI.models.recurring_sessions_models import SessionTemplate, GeneratedSession

# Find latest template
t = SessionTemplate.objects.order_by('-id').first()
print(f'Template: {t.title}')

# Delete generated sessions
gen = GeneratedSession.objects.filter(template=t)
print(f'Found {gen.count()} generated sessions')
gen.delete()
print('Deleted!')

# Reset last_generated
t.last_generated = None
t.save()
print('Reset last_generated')
