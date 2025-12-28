# backend/Education/Educational_system/eduAPI/signals/__init__.py
# Import signals to register them

from .recurring_sessions_signals import auto_generate_first_session

__all__ = ['auto_generate_first_session']
