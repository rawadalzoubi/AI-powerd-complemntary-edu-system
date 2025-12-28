# backend/Education/Educational_system/eduAPI/signals/recurring_sessions_signals.py
# Signals for automatic session generation

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from ..models.recurring_sessions_models import SessionTemplate
from ..services.session_generator import SessionGeneratorService


@receiver(post_save, sender=SessionTemplate)
def auto_generate_first_session(sender, instance, created, **kwargs):
    """
    Automatically generate the first session when a template is created
    if the start date is today and matches the day of week
    """
    if not created:
        return
    
    if instance.status != 'ACTIVE':
        return
    
    # Check if template has assignments
    if not instance.group_assignments.filter(is_active=True).exists():
        print(f"DEBUG: Template {instance.id} has no assignments yet, skipping auto-generation")
        return
    
    today = timezone.now().date()
    
    # Check if today matches the template schedule
    if today >= instance.start_date and today.weekday() == instance.day_of_week:
        print(f"DEBUG: Auto-generating first session for template {instance.id}")
        generator = SessionGeneratorService()
        try:
            result = generator.generate_sessions_for_date(today)
            print(f"DEBUG: Auto-generation result: {result}")
        except Exception as e:
            print(f"ERROR: Failed to auto-generate session: {str(e)}")
