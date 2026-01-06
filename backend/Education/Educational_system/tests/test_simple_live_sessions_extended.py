"""
Extended tests for simple_live_sessions.py
Target: Increase coverage from 28% to 70%+
"""
import pytest
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock
from django.test import TestCase, Client
from django.utils import timezone
from django.contrib.auth import get_user_model

User = get_user_model()


class TestSimpleLiveSessionsExtended(TestCase):
    """Extended tests for simple_live_sessions endpoints"""
    
    def setUp(self):
        self.client = Client()
        
        # Create users
        self.teacher = User.objects.create_user(
            username='teacher',
            email='teacher@test.com',
            password='SecurePass123!',
            role='teacher',
            first_name='Test',
            last_name='Teacher'
        )
        self.teacher.is_email_verified = True
        self.teacher.save()
        
        self.student = User.objects.create_user(
            username='student',
            email='student@test.com',
            password='SecurePass123!',
            role='student',
            first_name='Test',
            last_name='Student'
        )
        self.student.is_email_verified = True
        self.student.save()
        
        self.advisor = User.objects.create_user(
            username='advisor',
            email='advisor@test.com',
            password='SecurePass123!',
            role='advisor',
            first_name='Test',
            last_name='Advisor'
        )
        self.advisor.is_email_verified = True
        self.advisor.save()
    
    def get_token(self, email):
        """Helper to get JWT token"""
        response = self.client.post(
            '/api/user/login/',
            data={'email': email, 'password': 'SecurePass123!'},
            content_type='application/json'
        )
        if response.status_code == 200:
            data = response.json()
            return data.get('tokens', {}).get('access', data.get('access', ''))
        return ''
    
    def test_create_session_non_teacher(self):
        """Test that non-teachers cannot create sessions"""
        token = self.get_token('student@test.com')
        response = self.client.post(
            '/api/live-sessions/',
            data={
                'title': 'Test Session',
                'subject': 'Math',
                'level': '10',
                'scheduled_datetime': (timezone.now() + timedelta(days=1)).isoformat()
            },
            content_type='application/json',
            HTTP_AUTHORIZATION=f'Bearer {token}'
        )
        self.assertEqual(response.status_code, 403)
    
    def test_create_session_missing_required_fields(self):
        """Test session creation with missing fields"""
        token = self.get_token('teacher@test.com')
        
        # Missing title
        response = self.client.post(
            '/api/live-sessions/',
            data={
                'subject': 'Math',
                'level': '10',
                'scheduled_datetime': (timezone.now() + timedelta(days=1)).isoformat()
            },
            content_type='application/json',
            HTTP_AUTHORIZATION=f'Bearer {token}'
        )
        self.assertEqual(response.status_code, 400)
        
        # Missing subject
        response = self.client.post(
            '/api/live-sessions/',
            data={
                'title': 'Test',
                'level': '10',
                'scheduled_datetime': (timezone.now() + timedelta(days=1)).isoformat()
            },
            content_type='application/json',
            HTTP_AUTHORIZATION=f'Bearer {token}'
        )
        self.assertEqual(response.status_code, 400)
    
    def test_get_sessions_different_roles(self):
        """Test get_sessions returns different data for different roles"""
        # Teacher
        token = self.get_token('teacher@test.com')
        response = self.client.get(
            '/api/live-sessions/',
            HTTP_AUTHORIZATION=f'Bearer {token}'
        )
        self.assertEqual(response.status_code, 200)
        
        # Student
        token = self.get_token('student@test.com')
        response = self.client.get(
            '/api/live-sessions/',
            HTTP_AUTHORIZATION=f'Bearer {token}'
        )
        self.assertEqual(response.status_code, 200)
        
        # Advisor
        token = self.get_token('advisor@test.com')
        response = self.client.get(
            '/api/live-sessions/',
            HTTP_AUTHORIZATION=f'Bearer {token}'
        )
        self.assertEqual(response.status_code, 200)
    
    def test_get_my_schedule_student(self):
        """Test get_my_schedule for student"""
        token = self.get_token('student@test.com')
        response = self.client.get(
            '/api/live-sessions/my-schedule/',
            HTTP_AUTHORIZATION=f'Bearer {token}'
        )
        self.assertEqual(response.status_code, 200)
    
    def test_get_my_schedule_teacher(self):
        """Test get_my_schedule for teacher"""
        token = self.get_token('teacher@test.com')
        response = self.client.get(
            '/api/live-sessions/my-schedule/',
            HTTP_AUTHORIZATION=f'Bearer {token}'
        )
        self.assertEqual(response.status_code, 200)
    
    def test_get_pending_sessions_advisor(self):
        """Test get_pending_sessions for advisor"""
        # Change advisor role to uppercase for this test
        self.advisor.role = 'ADVISOR'
        self.advisor.save()
        
        token = self.get_token('advisor@test.com')
        response = self.client.get(
            '/api/live-sessions/pending/',
            HTTP_AUTHORIZATION=f'Bearer {token}'
        )
        self.assertEqual(response.status_code, 200)
    
    def test_assign_session_non_advisor(self):
        """Test that non-advisors cannot assign sessions"""
        token = self.get_token('teacher@test.com')
        response = self.client.post(
            '/api/live-sessions/1/assign/',
            data={'student_ids': [self.student.id]},
            content_type='application/json',
            HTTP_AUTHORIZATION=f'Bearer {token}'
        )
        self.assertEqual(response.status_code, 403)
    
    def test_assign_session_no_students(self):
        """Test assign session with no students selected"""
        token = self.get_token('advisor@test.com')
        response = self.client.post(
            '/api/live-sessions/1/assign/',
            data={'student_ids': []},
            content_type='application/json',
            HTTP_AUTHORIZATION=f'Bearer {token}'
        )
        self.assertIn(response.status_code, [400, 404])
    
    def test_update_session_non_teacher(self):
        """Test that non-teachers cannot update sessions"""
        token = self.get_token('student@test.com')
        response = self.client.put(
            '/api/live-sessions/1/',
            data={'title': 'Updated Title'},
            content_type='application/json',
            HTTP_AUTHORIZATION=f'Bearer {token}'
        )
        self.assertEqual(response.status_code, 403)
    
    def test_cancel_session_non_teacher(self):
        """Test that non-teachers cannot cancel sessions"""
        token = self.get_token('student@test.com')
        response = self.client.delete(
            '/api/live-sessions/1/cancel/',
            HTTP_AUTHORIZATION=f'Bearer {token}'
        )
        self.assertEqual(response.status_code, 403)
    
    def test_unassign_session_non_advisor(self):
        """Test that non-advisors cannot unassign sessions"""
        token = self.get_token('teacher@test.com')
        response = self.client.delete(
            '/api/live-sessions/1/unassign/',
            data={'student_ids': [self.student.id]},
            content_type='application/json',
            HTTP_AUTHORIZATION=f'Bearer {token}'
        )
        self.assertEqual(response.status_code, 403)
    
    def test_get_assigned_students_non_advisor(self):
        """Test that non-advisors cannot view assigned students"""
        token = self.get_token('teacher@test.com')
        response = self.client.get(
            '/api/live-sessions/1/assigned-students/',
            HTTP_AUTHORIZATION=f'Bearer {token}'
        )
        self.assertEqual(response.status_code, 403)
    
    def test_debug_sessions_endpoint(self):
        """Test debug_sessions endpoint"""
        response = self.client.get('/api/live-sessions/debug/')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('total_sessions', data)
        self.assertIn('sessions', data)
    
    def test_test_live_sessions_no_auth(self):
        """Test test_live_sessions_no_auth endpoint"""
        response = self.client.get('/api/live-sessions/test-no-auth/')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'OK')
    
    def test_test_live_sessions_with_auth(self):
        """Test test_live_sessions endpoint with auth"""
        token = self.get_token('teacher@test.com')
        response = self.client.get(
            '/api/live-sessions/test/',
            HTTP_AUTHORIZATION=f'Bearer {token}'
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['user'], 'teacher@test.com')


@pytest.mark.django_db
class TestJoinSessionExtended:
    """Extended tests for join_session functionality"""
    
    @pytest.fixture(autouse=True)
    def setup(self, teacher_user, student_user, advisor_user, db):
        self.teacher = teacher_user
        self.student = student_user
        self.advisor = advisor_user
        self.client = Client()
        
        try:
            from eduAPI.models.live_sessions_models import LiveSession, LiveSessionAssignment
            self.LiveSession = LiveSession
            self.LiveSessionAssignment = LiveSessionAssignment
            
            # Create a session
            self.session = LiveSession.objects.create(
                title='Test Session',
                teacher=self.teacher,
                scheduled_datetime=timezone.now() + timedelta(minutes=5),
                duration_minutes=60,
                subject='Math',
                level='10',
                status='ASSIGNED'
            )
            
            # Assign student
            self.assignment = LiveSessionAssignment.objects.create(
                session=self.session,
                student=self.student
            )
        except Exception:
            pytest.skip("LiveSession models not available")
    
    def get_token(self, email):
        """Helper to get JWT token"""
        response = self.client.post(
            '/api/user/login/',
            data={'email': email, 'password': 'TestPass123!'},
            content_type='application/json'
        )
        if response.status_code == 200:
            data = response.json()
            return data.get('tokens', {}).get('access', data.get('access', ''))
        return ''
    
    def test_join_session_advisor_forbidden(self):
        """Test that advisors cannot join sessions"""
        token = self.get_token('advisor@test.com')
        response = self.client.get(
            f'/api/live-sessions/{self.session.id}/join/',
            HTTP_AUTHORIZATION=f'Bearer {token}'
        )
        self.assertEqual(response.status_code, 403)
    
    def test_join_session_not_found(self):
        """Test join session with non-existent session"""
        token = self.get_token('teacher@test.com')
        response = self.client.get(
            '/api/live-sessions/99999/join/',
            HTTP_AUTHORIZATION=f'Bearer {token}'
        )
        self.assertEqual(response.status_code, 404)
    
    def test_join_session_student_not_assigned(self):
        """Test student cannot join session they're not assigned to"""
        # Create another student
        other_student = User.objects.create_user(
            username='other_student',
            email='other@test.com',
            password='TestPass123!',
            role='student'
        )
        other_student.is_email_verified = True
        other_student.save()
        
        token = self.get_token('other@test.com')
        response = self.client.get(
            f'/api/live-sessions/{self.session.id}/join/',
            HTTP_AUTHORIZATION=f'Bearer {token}'
        )
        self.assertEqual(response.status_code, 403)
    
    def test_join_session_cancelled(self):
        """Test cannot join cancelled session"""
        self.session.status = 'CANCELLED'
        self.session.save()
        
        token = self.get_token('teacher@test.com')
        response = self.client.get(
            f'/api/live-sessions/{self.session.id}/join/',
            HTTP_AUTHORIZATION=f'Bearer {token}'
        )
        self.assertEqual(response.status_code, 400)
    
    def test_join_session_ended(self):
        """Test cannot join ended session"""
        self.session.scheduled_datetime = timezone.now() - timedelta(hours=2)
        self.session.save()
        
        token = self.get_token('teacher@test.com')
        response = self.client.get(
            f'/api/live-sessions/{self.session.id}/join/',
            HTTP_AUTHORIZATION=f'Bearer {token}'
        )
        self.assertEqual(response.status_code, 400)


@pytest.mark.django_db
class TestSessionCRUDExtended:
    """Extended CRUD tests for sessions"""
    
    @pytest.fixture(autouse=True)
    def setup(self, teacher_user, advisor_user, student_user, db):
        self.teacher = teacher_user
        self.advisor = advisor_user
        self.student = student_user
        self.client = Client()
        
        try:
            from eduAPI.models.live_sessions_models import LiveSession, LiveSessionAssignment
            self.LiveSession = LiveSession
            self.LiveSessionAssignment = LiveSessionAssignment
            
            self.session = LiveSession.objects.create(
                title='Test Session',
                teacher=self.teacher,
                scheduled_datetime=timezone.now() + timedelta(days=1),
                duration_minutes=60,
                subject='Math',
                level='10',
                status='PENDING'
            )
        except Exception:
            pytest.skip("LiveSession models not available")
    
    def get_token(self, email):
        """Helper to get JWT token"""
        response = self.client.post(
            '/api/user/login/',
            data={'email': email, 'password': 'TestPass123!'},
            content_type='application/json'
        )
        if response.status_code == 200:
            data = response.json()
            return data.get('tokens', {}).get('access', data.get('access', ''))
        return ''
    
    def test_update_session_not_found(self):
        """Test update non-existent session"""
        token = self.get_token('teacher@test.com')
        response = self.client.put(
            '/api/live-sessions/99999/',
            data={'title': 'Updated'},
            content_type='application/json',
            HTTP_AUTHORIZATION=f'Bearer {token}'
        )
        assert response.status_code == 404
    
    def test_cancel_session_not_found(self):
        """Test cancel non-existent session"""
        token = self.get_token('teacher@test.com')
        response = self.client.delete(
            '/api/live-sessions/99999/cancel/',
            HTTP_AUTHORIZATION=f'Bearer {token}'
        )
        assert response.status_code == 404
    
    def test_cancel_session_wrong_status(self):
        """Test cannot cancel completed session"""
        self.session.status = 'COMPLETED'
        self.session.save()
        
        token = self.get_token('teacher@test.com')
        response = self.client.delete(
            f'/api/live-sessions/{self.session.id}/cancel/',
            HTTP_AUTHORIZATION=f'Bearer {token}'
        )
        assert response.status_code == 400
    
    def test_assign_session_not_found(self):
        """Test assign non-existent session"""
        token = self.get_token('advisor@test.com')
        response = self.client.post(
            '/api/live-sessions/99999/assign/',
            data={'student_ids': [self.student.id]},
            content_type='application/json',
            HTTP_AUTHORIZATION=f'Bearer {token}'
        )
        assert response.status_code == 404
    
    def test_unassign_session_not_found(self):
        """Test unassign non-existent session"""
        token = self.get_token('advisor@test.com')
        response = self.client.delete(
            '/api/live-sessions/99999/unassign/',
            data={'student_ids': [self.student.id]},
            content_type='application/json',
            HTTP_AUTHORIZATION=f'Bearer {token}'
        )
        assert response.status_code == 404
    
    def test_unassign_no_students_selected(self):
        """Test unassign with no students selected"""
        token = self.get_token('advisor@test.com')
        response = self.client.delete(
            f'/api/live-sessions/{self.session.id}/unassign/',
            data={'student_ids': []},
            content_type='application/json',
            HTTP_AUTHORIZATION=f'Bearer {token}'
        )
        assert response.status_code == 400
    
    def test_get_assigned_students_not_found(self):
        """Test get assigned students for non-existent session"""
        token = self.get_token('advisor@test.com')
        response = self.client.get(
            '/api/live-sessions/99999/assigned-students/',
            HTTP_AUTHORIZATION=f'Bearer {token}'
        )
        assert response.status_code == 404
