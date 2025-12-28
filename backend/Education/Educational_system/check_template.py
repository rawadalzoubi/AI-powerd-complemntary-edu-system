import os
import django
import datetime

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'edu_system.settings')
django.setup()

from eduAPI.models.recurring_sessions_models import SessionTemplate

t = SessionTemplate.objects.filter(title='TESTNOW').first()
if t:
    print(f'Template: {t.title}')
    print(f'Day of week: {t.day_of_week} - {t.get_day_of_week_display()}')
    print(f'Start time: {t.start_time}')
    print(f'Start date: {t.start_date}')
    print(f'Last generated: {t.last_generated}')
    print(f'Status: {t.status}')
    print(f'Today: {datetime.date.today()} - weekday: {datetime.date.today().weekday()}')
    print(f'Match: {datetime.date.today().weekday() == t.day_of_week}')
    
    # Day mapping
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    print(f'\nTemplate expects: {days[t.day_of_week]}')
    print(f'Today is: {days[datetime.date.today().weekday()]}')
    
    # Check next_generation_date
    print(f'\nNext generation date: {t.next_generation_date}')
    if t.next_generation_date:
        days_diff = (t.next_generation_date - datetime.date.today()).days
        print(f'Days until next generation: {days_diff}')
    
    # Check if start_date is in past
    if t.start_date < datetime.date.today():
        print(f'\n⚠️ WARNING: Start date {t.start_date} is in the PAST!')
        print(f'   Days ago: {(datetime.date.today() - t.start_date).days}')
        print(f'   This template should have its start_date updated to today or a future date')
else:
    print('Template not found')
