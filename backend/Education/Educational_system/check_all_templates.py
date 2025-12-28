import os
import django
import datetime

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'edu_system.settings')
django.setup()

from eduAPI.models.recurring_sessions_models import SessionTemplate

templates = SessionTemplate.objects.all().order_by('-created_at')

print(f'Found {templates.count()} templates:\n')

for t in templates:
    print(f'=' * 80)
    print(f'Template: {t.title}')
    print(f'Status: {t.status}')
    print(f'Day: {t.get_day_of_week_display()} ({t.day_of_week})')
    print(f'Time: {t.start_time}')
    print(f'Duration: {t.duration_minutes} minutes')
    print(f'Start date: {t.start_date}')
    print(f'Last generated: {t.last_generated}')
    print(f'Next generation: {t.next_generation_date}')
    
    if t.next_generation_date:
        days_diff = (t.next_generation_date - datetime.date.today()).days
        print(f'Days until next: {days_diff}')
    
    if t.start_date < datetime.date.today():
        print(f'⚠️ Start date is {(datetime.date.today() - t.start_date).days} days in the past')
    
    print()
