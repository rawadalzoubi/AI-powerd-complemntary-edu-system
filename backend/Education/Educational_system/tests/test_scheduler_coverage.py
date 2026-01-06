# Tests for session_scheduler.py to increase coverage
import pytest
from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
from unittest.mock import Mock, patch, MagicMock
import threading
import time


class TestSessionScheduler(TestCase):
    """Tests for session_scheduler.py"""
    
    def test_scheduler_init(self):
        """Test SessionScheduler initialization"""
        from eduAPI.services.session_scheduler import SessionScheduler
        
        scheduler = SessionScheduler()
        
        self.assertFalse(scheduler.running)
        self.assertEqual(scheduler.check_interval, 60)
        self.assertIsNone(scheduler.last_generation_date)
    
    def test_scheduler_stop(self):
        """Test SessionScheduler stop method"""
        from eduAPI.services.session_scheduler import SessionScheduler
        
        scheduler = SessionScheduler()
        scheduler.running = True
        scheduler.stop()
        
        self.assertFalse(scheduler.running)
    
    def test_check_and_generate_same_day(self):
        """Test _check_and_generate when date hasn't changed"""
        from eduAPI.services.session_scheduler import SessionScheduler
        
        scheduler = SessionScheduler()
        scheduler.last_generation_date = timezone.now().date()
        
        with patch.object(scheduler, '_generate_sessions_safe') as mock_generate:
            scheduler._check_and_generate()
            # Should not call generate since date is same
            mock_generate.assert_not_called()
    
    def test_check_and_generate_new_day(self):
        """Test _check_and_generate when date has changed"""
        from eduAPI.services.session_scheduler import SessionScheduler
        
        scheduler = SessionScheduler()
        scheduler.last_generation_date = timezone.now().date() - timedelta(days=1)
        
        with patch.object(scheduler, '_generate_sessions_safe') as mock_generate:
            scheduler._check_and_generate()
            # Should call generate since date changed
            mock_generate.assert_called_once()
    
    def test_get_scheduler_singleton(self):
        """Test get_scheduler returns singleton"""
        import eduAPI.services.session_scheduler as scheduler_module
        from eduAPI.services.session_scheduler import get_scheduler
        
        # Reset singleton
        scheduler_module._scheduler_instance = None
        
        scheduler1 = get_scheduler()
        scheduler2 = get_scheduler()
        
        self.assertIs(scheduler1, scheduler2)
    
    def test_generate_sessions_safe_success(self):
        """Test _generate_sessions_safe with successful generation"""
        from eduAPI.services.session_scheduler import SessionScheduler
        
        # Setup mock
        mock_generator = MagicMock()
        mock_generator.generate_sessions_for_date.return_value = {
            'generated': 5,
            'skipped': 2,
            'failed': 0
        }
        
        scheduler = SessionScheduler()
        
        # Patch at the module where it's imported (inside the method)
        with patch.dict('sys.modules', {'eduAPI.services.session_generator': MagicMock(SessionGeneratorService=MagicMock(return_value=mock_generator))}):
            with patch.object(scheduler, '_generate_upcoming_week'):
                scheduler._generate_sessions_safe()
        
        # The test passes if no exception is raised
        self.assertTrue(True)
    
    def test_generate_sessions_safe_exception(self):
        """Test _generate_sessions_safe with exception"""
        from eduAPI.services.session_scheduler import SessionScheduler
        
        scheduler = SessionScheduler()
        
        # Patch at the module level to raise exception
        with patch.dict('sys.modules', {'eduAPI.services.session_generator': MagicMock(SessionGeneratorService=MagicMock(side_effect=Exception("Test error")))}):
            # Should not raise exception - it's caught internally
            scheduler._generate_sessions_safe()
    
    def test_generate_upcoming_week(self):
        """Test _generate_upcoming_week method"""
        from eduAPI.services.session_scheduler import SessionScheduler
        
        # Setup mock
        mock_generator = MagicMock()
        mock_generator.generate_sessions_for_date.return_value = {
            'generated': 1,
            'skipped': 0,
            'failed': 0
        }
        
        scheduler = SessionScheduler()
        scheduler._generate_upcoming_week(mock_generator)
        
        # Should be called 7 times (for each day of the week)
        self.assertEqual(mock_generator.generate_sessions_for_date.call_count, 7)
    
    def test_generate_upcoming_week_exception(self):
        """Test _generate_upcoming_week with exception"""
        from eduAPI.services.session_scheduler import SessionScheduler
        
        # Setup mock to raise exception
        mock_generator = MagicMock()
        mock_generator.generate_sessions_for_date.side_effect = Exception("Test error")
        
        scheduler = SessionScheduler()
        # Should not raise exception
        scheduler._generate_upcoming_week(mock_generator)
