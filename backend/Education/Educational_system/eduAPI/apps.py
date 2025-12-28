from django.apps import AppConfig
import os
import threading


class EduapiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'eduAPI'
    verbose_name = 'EduAPI'
    
    def ready(self):
        """Import signals when app is ready and start session scheduler"""
        import eduAPI.signals
        
        # تجنب التشغيل المزدوج (Django يشغل ready مرتين أحياناً)
        # وتجنب التشغيل في management commands
        if os.environ.get('RUN_MAIN') == 'true':
            self._start_session_scheduler()
    
    def _start_session_scheduler(self):
        """Start the background session generator"""
        from .services.session_scheduler import SessionScheduler
        
        # تشغيل الـ scheduler في thread منفصل
        scheduler = SessionScheduler()
        scheduler_thread = threading.Thread(target=scheduler.start, daemon=True)
        scheduler_thread.start()
        print("✅ Session Scheduler started automatically")
