# Tests for simple_live_sessions.py to increase coverage
import pytest
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta

User = get_user_model()


class TestJoinSessionExtended(TestCase):
    """Extended tests for join_session endpoint"""
    
    def setUp(self):
        self.client = APIClient()
        self.teacher = User.objects.create_user(
            username='teacher_js1',
            email='teacher@test.com',
            password='testpass123',
            first_name='Test',
            last_name='Teacher',
            role='teacher',
            is_email_verified=True
        )
        self.advisor = User.objects.create_user(
            username='advisor_js1',
            email='advisor@test.com',
            password='testpass123',
            first_name='Test',
            last_name='Advisor',
            role='advisor',
            is_email_verified=True
        )
        self.student = User.objects.create_user(
            username='student_js1',
            email='student@test.com',
            password='testpass123',
            first_name='Test',
            last_name='Student',
            role='student',
            is_email_verified=True
        )
    
    def test_join_session_as_advisor(self):
        """Test that advisors cannot join sessions"""
        from eduAPI.models.live_sessions_models import LiveSession
        
        session = LiveSession.objects.create(
            title='Test Session',
            teacher=self.teacher,
            subject='Math',
            level='10',
            scheduled_datetime=timezone.now() + timedelta(hours=1),
            duration_minutes=60,
            status='ASSIGNED'
        )
        
        self.client.force_authenticate(user=self.advisor)
        response = self.client.get(f'/api/live-sessions/{session.id}/join/')
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_join_session_teacher_not_owner(self):
        """Test teacher cannot join session they don't own"""
        from eduAPI.models.live_sessions_models import LiveSession
        
        teacher2 = User.objects.create_user(
            username='teacher_js2',
            email='teacher2@test.com',
            password='testpass123',
            first_name='Test2',
            last_name='Teacher2',
            role='teacher',
            is_email_verified=True
        )
        
        session = LiveSession.objects.create(
            title='Test Session',
            teacher=self.teacher,
            subject='Math',
            level='10',
            scheduled_datetime=timezone.now() + timedelta(hours=1),
            duration_minutes=60,
            status='ASSIGNED'
        )
        
        self.client.force_authenticate(user=teacher2)
        response = self.client.get(f'/api/live-sessions/{session.id}/join/')
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_join_session_student_not_assigned(self):
        """Test student cannot join session they're not assigned to"""
        from eduAPI.models.live_sessions_models import LiveSession
        
        session = LiveSession.objects.create(
            title='Test Session',
            teacher=self.teacher,
            subject='Math',
            level='10',
            scheduled_datetime=timezone.now() + timedelta(hours=1),
            duration_minutes=60,
            status='ASSIGNED'
        )
        
        self.client.force_authenticate(user=self.student)
        response = self.client.get(f'/api/live-sessions/{session.id}/join/')
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_join_session_cancelled(self):
        """Test cannot join cancelled session"""
        from eduAPI.models.live_sessions_models import LiveSession
        
        session = LiveSession.objects.create(
            title='Test Session',
            teacher=self.teacher,
            subject='Math',
            level='10',
            scheduled_datetime=timezone.now() + timedelta(hours=1),
            duration_minutes=60,
            status='CANCELLED'
        )
        
        self.client.force_authenticate(user=self.teacher)
        response = self.client.get(f'/api/live-sessions/{session.id}/join/')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_join_session_ended(self):
        """Test cannot join ended session"""
        from eduAPI.models.live_sessions_models import LiveSession
        
        session = LiveSession.objects.create(
            title='Test Session',
            teacher=self.teacher,
            subject='Math',
            level='10',
            scheduled_datetime=timezone.now() - timedelta(hours=2),
            duration_minutes=60,
            status='ASSIGNED'
        )
        
        self.client.force_authenticate(user=self.teacher)
        response = self.client.get(f'/api/live-sessions/{session.id}/join/')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_join_session_teacher_too_early(self):
        """Test teacher cannot join too early"""
        from eduAPI.models.live_sessions_models import LiveSession
        
        session = LiveSession.objects.create(
            title='Test Session',
            teacher=self.teacher,
            subject='Math',
            level='10',
            scheduled_datetime=timezone.now() + timedelta(hours=2),
            duration_minutes=60,
            status='ASSIGNED'
        )
        
        self.client.force_authenticate(user=self.teacher)
        response = self.client.get(f'/api/live-sessions/{session.id}/join/')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_join_session_student_too_early(self):
        """Test student cannot join before session starts"""
        from eduAPI.models.live_sessions_models import LiveSession, LiveSessionAssignment
        
        session = LiveSession.objects.create(
            title='Test Session',
            teacher=self.teacher,
            subject='Math',
            level='10',
            scheduled_datetime=timezone.now() + timedelta(hours=1),
            duration_minutes=60,
            status='ASSIGNED'
        )
        
        LiveSessionAssignment.objects.create(
            session=session,
            student=self.student,
            advisor=self.advisor
        )
        
        self.client.force_authenticate(user=self.student)
        response = self.client.get(f'/api/live-sessions/{session.id}/join/')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_join_session_student_late(self):
        """Test student cannot join after late window"""
        from eduAPI.models.live_sessions_models import LiveSession, LiveSessionAssignment
        
        session = LiveSession.objects.create(
            title='Test Session',
            teacher=self.teacher,
            subject='Math',
            level='10',
            scheduled_datetime=timezone.now() - timedelta(minutes=15),
            duration_minutes=60,
            status='ASSIGNED'
        )
        
        LiveSessionAssignment.objects.create(
            session=session,
            student=self.student,
            advisor=self.advisor
        )
        
        self.client.force_authenticate(user=self.student)
        response = self.client.get(f'/api/live-sessions/{session.id}/join/')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_join_session_student_success(self):
        """Test student can join within window"""
        from eduAPI.models.live_sessions_models import LiveSession, LiveSessionAssignment
        
        session = LiveSession.objects.create(
            title='Test Session',
            teacher=self.teacher,
            subject='Math',
            level='10',
            scheduled_datetime=timezone.now() - timedelta(minutes=5),
            duration_minutes=60,
            status='ASSIGNED'
        )
        
        LiveSessionAssignment.objects.create(
            session=session,
            student=self.student,
            advisor=self.advisor
        )
        
        self.client.force_authenticate(user=self.student)
        response = self.client.get(f'/api/live-sessions/{session.id}/join/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('meeting_url', response.data)
    
    def test_join_session_teacher_success(self):
        """Test teacher can join within window"""
        from eduAPI.models.live_sessions_models import LiveSession
        
        session = LiveSession.objects.create(
            title='Test Session',
            teacher=self.teacher,
            subject='Math',
            level='10',
            scheduled_datetime=timezone.now() + timedelta(minutes=10),
            duration_minutes=60,
            status='ASSIGNED'
        )
        
        self.client.force_authenticate(user=self.teacher)
        response = self.client.get(f'/api/live-sessions/{session.id}/join/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('meeting_url', response.data)
    
    def test_join_session_not_found(self):
        """Test joining non-existent session"""
        self.client.force_authenticate(user=self.teacher)
        response = self.client.get('/api/live-sessions/99999/join/')
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class TestGetPendingSessions(TestCase):
    """Tests for get_pending_sessions endpoint"""
    
    def setUp(self):
        self.client = APIClient()
        self.advisor = User.objects.create_user(
            username='advisor_ps1',
            email='advisor@test.com',
            password='testpass123',
            first_name='Test',
            last_name='Advisor',
            role='advisor',
            is_email_verified=True
        )
        self.student = User.objects.create_user(
            username='student_ps1',
            email='student@test.com',
            password='testpass123',
            first_name='Test',
            last_name='Student',
            role='student',
            is_email_verified=True
        )
    
    def test_get_pending_sessions_as_advisor(self):
        """Test getting pending sessions as advisor"""
        self.client.force_authenticate(user=self.advisor)
        response = self.client.get('/api/live-sessions/pending/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_get_pending_sessions_as_non_advisor(self):
        """Test getting pending sessions as non-advisor"""
        self.client.force_authenticate(user=self.student)
        response = self.client.get('/api/live-sessions/pending/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)


class TestUnassignSession(TestCase):
    """Tests for unassign_session endpoint"""
    
    def setUp(self):
        self.client = APIClient()
        self.teacher = User.objects.create_user(
            username='teacher_us1',
            email='teacher@test.com',
            password='testpass123',
            first_name='Test',
            last_name='Teacher',
            role='teacher',
            is_email_verified=True
        )
        self.advisor = User.objects.create_user(
            username='advisor_us1',
            email='advisor@test.com',
            password='testpass123',
            first_name='Test',
            last_name='Advisor',
            role='advisor',
            is_email_verified=True
        )
        self.student = User.objects.create_user(
            username='student_us1',
            email='student@test.com',
            password='testpass123',
            first_name='Test',
            last_name='Student',
            role='student',
            is_email_verified=True
        )
    
    def test_unassign_session_not_advisor(self):
        """Test unassigning by non-advisor"""
        from eduAPI.models.live_sessions_models import LiveSession
        
        session = LiveSession.objects.create(
            title='Test Session',
            teacher=self.teacher,
            subject='Math',
            level='10',
            scheduled_datetime=timezone.now() + timedelta(hours=1),
            duration_minutes=60,
            status='ASSIGNED'
        )
        
        self.client.force_authenticate(user=self.teacher)
        response = self.client.delete(
            f'/api/live-sessions/{session.id}/unassign/',
            {'student_ids': [self.student.id]},
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_unassign_session_no_students(self):
        """Test unassigning with no students"""
        from eduAPI.models.live_sessions_models import LiveSession
        
        session = LiveSession.objects.create(
            title='Test Session',
            teacher=self.teacher,
            subject='Math',
            level='10',
            scheduled_datetime=timezone.now() + timedelta(hours=1),
            duration_minutes=60,
            status='ASSIGNED'
        )
        
        self.client.force_authenticate(user=self.advisor)
        response = self.client.delete(
            f'/api/live-sessions/{session.id}/unassign/',
            {'student_ids': []},
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_unassign_session_success(self):
        """Test successful unassignment"""
        from eduAPI.models.live_sessions_models import LiveSession, LiveSessionAssignment
        
        session = LiveSession.objects.create(
            title='Test Session',
            teacher=self.teacher,
            subject='Math',
            level='10',
            scheduled_datetime=timezone.now() + timedelta(hours=1),
            duration_minutes=60,
            status='ASSIGNED'
        )
        
        LiveSessionAssignment.objects.create(
            session=session,
            student=self.student,
            advisor=self.advisor
        )
        
        self.client.force_authenticate(user=self.advisor)
        response = self.client.delete(
            f'/api/live-sessions/{session.id}/unassign/',
            {'student_ids': [self.student.id]},
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['removed_assignments'], 1)
    
    def test_unassign_session_not_found(self):
        """Test unassigning from non-existent session"""
        self.client.force_authenticate(user=self.advisor)
        response = self.client.delete(
            '/api/live-sessions/99999/unassign/',
            {'student_ids': [self.student.id]},
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class TestUpdateSession(TestCase):
    """Tests for update_session endpoint"""
    
    def setUp(self):
        self.client = APIClient()
        self.teacher = User.objects.create_user(
            username='teacher_upd1',
            email='teacher@test.com',
            password='testpass123',
            first_name='Test',
            last_name='Teacher',
            role='teacher',
            is_email_verified=True
        )
        self.student = User.objects.create_user(
            username='student_upd1',
            email='student@test.com',
            password='testpass123',
            first_name='Test',
            last_name='Student',
            role='student',
            is_email_verified=True
        )
    
    def test_update_session_not_teacher(self):
        """Test updating by non-teacher"""
        from eduAPI.models.live_sessions_models import LiveSession
        
        session = LiveSession.objects.create(
            title='Test Session',
            teacher=self.teacher,
            subject='Math',
            level='10',
            scheduled_datetime=timezone.now() + timedelta(hours=1),
            duration_minutes=60,
            status='PENDING'
        )
        
        self.client.force_authenticate(user=self.student)
        response = self.client.put(
            f'/api/live-sessions/{session.id}/',
            {'title': 'Updated Title'},
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_update_session_success(self):
        """Test successful update"""
        from eduAPI.models.live_sessions_models import LiveSession
        
        session = LiveSession.objects.create(
            title='Test Session',
            teacher=self.teacher,
            subject='Math',
            level='10',
            scheduled_datetime=timezone.now() + timedelta(hours=1),
            duration_minutes=60,
            status='PENDING'
        )
        
        self.client.force_authenticate(user=self.teacher)
        response = self.client.put(
            f'/api/live-sessions/{session.id}/',
            {'title': 'Updated Title', 'description': 'New description'},
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Updated Title')


class TestCancelSession(TestCase):
    """Tests for cancel_session endpoint"""
    
    def setUp(self):
        self.client = APIClient()
        self.teacher = User.objects.create_user(
            username='teacher_cs1',
            email='teacher@test.com',
            password='testpass123',
            first_name='Test',
            last_name='Teacher',
            role='teacher',
            is_email_verified=True
        )
        self.student = User.objects.create_user(
            username='student_cs1',
            email='student@test.com',
            password='testpass123',
            first_name='Test',
            last_name='Student',
            role='student',
            is_email_verified=True
        )
    
    def test_cancel_session_not_teacher(self):
        """Test cancelling by non-teacher"""
        from eduAPI.models.live_sessions_models import LiveSession
        
        session = LiveSession.objects.create(
            title='Test Session',
            teacher=self.teacher,
            subject='Math',
            level='10',
            scheduled_datetime=timezone.now() + timedelta(hours=1),
            duration_minutes=60,
            status='PENDING'
        )
        
        self.client.force_authenticate(user=self.student)
        response = self.client.delete(f'/api/live-sessions/{session.id}/cancel/')
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_cancel_session_wrong_status(self):
        """Test cancelling session with wrong status"""
        from eduAPI.models.live_sessions_models import LiveSession
        
        session = LiveSession.objects.create(
            title='Test Session',
            teacher=self.teacher,
            subject='Math',
            level='10',
            scheduled_datetime=timezone.now() + timedelta(hours=1),
            duration_minutes=60,
            status='COMPLETED'
        )
        
        self.client.force_authenticate(user=self.teacher)
        response = self.client.delete(f'/api/live-sessions/{session.id}/cancel/')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class TestGetAssignedStudents(TestCase):
    """Tests for get_assigned_students endpoint"""
    
    def setUp(self):
        self.client = APIClient()
        self.teacher = User.objects.create_user(
            username='teacher_gas1',
            email='teacher@test.com',
            password='testpass123',
            first_name='Test',
            last_name='Teacher',
            role='teacher',
            is_email_verified=True
        )
        self.advisor = User.objects.create_user(
            username='advisor_gas1',
            email='advisor@test.com',
            password='testpass123',
            first_name='Test',
            last_name='Advisor',
            role='advisor',
            is_email_verified=True
        )
        self.student = User.objects.create_user(
            username='student_gas1',
            email='student@test.com',
            password='testpass123',
            first_name='Test',
            last_name='Student',
            role='student',
            is_email_verified=True
        )
    
    def test_get_assigned_students_not_advisor(self):
        """Test getting assigned students by non-advisor"""
        from eduAPI.models.live_sessions_models import LiveSession
        
        session = LiveSession.objects.create(
            title='Test Session',
            teacher=self.teacher,
            subject='Math',
            level='10',
            scheduled_datetime=timezone.now() + timedelta(hours=1),
            duration_minutes=60,
            status='ASSIGNED'
        )
        
        self.client.force_authenticate(user=self.teacher)
        response = self.client.get(f'/api/live-sessions/{session.id}/assigned-students/')
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_get_assigned_students_success(self):
        """Test getting assigned students successfully"""
        from eduAPI.models.live_sessions_models import LiveSession, LiveSessionAssignment
        
        session = LiveSession.objects.create(
            title='Test Session',
            teacher=self.teacher,
            subject='Math',
            level='10',
            scheduled_datetime=timezone.now() + timedelta(hours=1),
            duration_minutes=60,
            status='ASSIGNED'
        )
        
        LiveSessionAssignment.objects.create(
            session=session,
            student=self.student,
            advisor=self.advisor
        )
        
        self.client.force_authenticate(user=self.advisor)
        response = self.client.get(f'/api/live-sessions/{session.id}/assigned-students/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total_assigned'], 1)


class TestAssignSession(TestCase):
    """Tests for assign_session endpoint"""
    
    def setUp(self):
        self.client = APIClient()
        self.teacher = User.objects.create_user(
            username='teacher_as1',
            email='teacher@test.com',
            password='testpass123',
            first_name='Test',
            last_name='Teacher',
            role='teacher',
            is_email_verified=True
        )
        self.advisor = User.objects.create_user(
            username='advisor_as1',
            email='advisor@test.com',
            password='testpass123',
            first_name='Test',
            last_name='Advisor',
            role='advisor',
            is_email_verified=True
        )
        self.student = User.objects.create_user(
            username='student_as1',
            email='student@test.com',
            password='testpass123',
            first_name='Test',
            last_name='Student',
            role='student',
            is_email_verified=True
        )
    
    def test_assign_session_not_advisor(self):
        """Test assigning by non-advisor"""
        from eduAPI.models.live_sessions_models import LiveSession
        
        session = LiveSession.objects.create(
            title='Test Session',
            teacher=self.teacher,
            subject='Math',
            level='10',
            scheduled_datetime=timezone.now() + timedelta(hours=1),
            duration_minutes=60,
            status='PENDING'
        )
        
        self.client.force_authenticate(user=self.teacher)
        response = self.client.post(
            f'/api/live-sessions/{session.id}/assign/',
            {'student_ids': [self.student.id]},
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_assign_session_no_students(self):
        """Test assigning with no students"""
        from eduAPI.models.live_sessions_models import LiveSession
        
        session = LiveSession.objects.create(
            title='Test Session',
            teacher=self.teacher,
            subject='Math',
            level='10',
            scheduled_datetime=timezone.now() + timedelta(hours=1),
            duration_minutes=60,
            status='PENDING'
        )
        
        self.client.force_authenticate(user=self.advisor)
        response = self.client.post(
            f'/api/live-sessions/{session.id}/assign/',
            {'student_ids': []},
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_assign_session_already_assigned(self):
        """Test assigning already assigned student"""
        from eduAPI.models.live_sessions_models import LiveSession, LiveSessionAssignment
        
        session = LiveSession.objects.create(
            title='Test Session',
            teacher=self.teacher,
            subject='Math',
            level='10',
            scheduled_datetime=timezone.now() + timedelta(hours=1),
            duration_minutes=60,
            status='PENDING'
        )
        
        LiveSessionAssignment.objects.create(
            session=session,
            student=self.student,
            advisor=self.advisor
        )
        
        self.client.force_authenticate(user=self.advisor)
        response = self.client.post(
            f'/api/live-sessions/{session.id}/assign/',
            {'student_ids': [self.student.id]},
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['new_assignments'], 0)
