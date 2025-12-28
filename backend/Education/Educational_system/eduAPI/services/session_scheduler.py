# backend/Education/Educational_system/eduAPI/services/session_scheduler.py
# Background scheduler for automatic session generation

import time
import threading
from datetime import datetime, timedelta
from django.utils import timezone


class SessionScheduler:
    """
    Background scheduler that automatically generates sessions
    - يشتغل تلقائياً لما يبدأ السيرفر
    - يولد الجلسات لليوم الحالي
    - يتحقق كل ساعة من جلسات جديدة
    """
    
    def __init__(self):
        self.running = False
        self.check_interval = 60  # كل ساعة (بالثواني)
        self.last_generation_date = None
    
    def start(self):
        """Start the scheduler"""
        self.running = True
        print(f"🚀 Session Scheduler starting at {timezone.now()}")
        
        # انتظر قليلاً للتأكد من جاهزية Django
        time.sleep(5)
        
        # توليد الجلسات فوراً عند بدء السيرفر
        self._generate_sessions_safe()
        
        # حلقة التحقق الدوري
        while self.running:
            time.sleep(self.check_interval)
            self._check_and_generate()
    
    def stop(self):
        """Stop the scheduler"""
        self.running = False
        print("🛑 Session Scheduler stopped")
    
    def _check_and_generate(self):
        """Check if we need to generate sessions"""
        today = timezone.now().date()
        
        # إذا تغير اليوم، ولّد جلسات جديدة
        if self.last_generation_date != today:
            print(f"📅 New day detected: {today}")
            self._generate_sessions_safe()
    
    def _generate_sessions_safe(self):
        """Generate sessions with error handling"""
        try:
            from .session_generator import SessionGeneratorService
            
            generator = SessionGeneratorService()
            today = timezone.now().date()
            
            print(f"⏳ Generating sessions for {today}...")
            result = generator.generate_sessions_for_date(today)
            
            self.last_generation_date = today
            
            print(f"✅ Session generation complete:")
            print(f"   - Generated: {result['generated']}")
            print(f"   - Skipped: {result['skipped']}")
            print(f"   - Failed: {result['failed']}")
            
            # توليد جلسات الأسبوع القادم (اختياري)
            self._generate_upcoming_week(generator)
            
        except Exception as e:
            print(f"❌ Session generation error: {str(e)}")
    
    def _generate_upcoming_week(self, generator):
        """Generate sessions for the upcoming week"""
        try:
            today = timezone.now().date()
            total_generated = 0
            
            for i in range(1, 8):  # الأيام السبعة القادمة
                future_date = today + timedelta(days=i)
                result = generator.generate_sessions_for_date(future_date)
                total_generated += result['generated']
            
            if total_generated > 0:
                print(f"📆 Generated {total_generated} sessions for upcoming week")
                
        except Exception as e:
            print(f"⚠️ Upcoming week generation error: {str(e)}")


# Singleton instance
_scheduler_instance = None

def get_scheduler():
    """Get or create scheduler instance"""
    global _scheduler_instance
    if _scheduler_instance is None:
        _scheduler_instance = SessionScheduler()
    return _scheduler_instance
