"""
Comprehensive tests for advisor_management.py
Target: Increase coverage from 31% to 90%+
Tests the functions directly since URLs may not be registered
"""
import pytest
from unittest.mock import patch, MagicMock, Mock
from django.test import TestCase, Client, RequestFactory
from django.contrib.auth import get_user_model
from django.contrib.messages.storage.fallback import FallbackStorage
from django.contrib.sessions.middleware import SessionMiddleware

User = get_user_model()


def add_middleware_to_request(request):
    """Helper to add session and messages middleware to request"""
    middleware = SessionMiddleware(lambda x: None)
    middleware.process_request(request)
    request.session.save()
    
    messages = FallbackStorage(request)
    setattr(request, '_messages', messages)
    return request


@pytest.mark.django_db
class TestSuperuserRequired:
    """Tests for superuser_required decorator function"""
    
    def test_superuser_required_with_superuser(self, admin_user):
        """Test superuser_required returns True for superuser"""
        from eduAPI.views.advisor_management import superuser_required
        assert superuser_required(admin_user) is True
    
    def test_superuser_required_with_admin_role(self, db):
        """Test superuser_required returns True for admin role"""
        from eduAPI.views.advisor_management import superuser_required
        user = User.objects.create_user(
            email='admin@test.com',
            username='admin',
            password='testpass123',
            role='admin'
        )
        assert superuser_required(user) is True
    
    def test_superuser_required_with_regular_user(self, student_user):
        """Test superuser_required returns False for regular user"""
        from eduAPI.views.advisor_management import superuser_required
        assert superuser_required(student_user) is False
    
    def test_superuser_required_with_anonymous_user(self):
        """Test superuser_required returns False for anonymous user"""
        from eduAPI.views.advisor_management import superuser_required
        from django.contrib.auth.models import AnonymousUser
        assert superuser_required(AnonymousUser()) is False


@pytest.mark.django_db
class TestAdvisorListView:
    """Tests for advisor_list view function"""
    
    @pytest.fixture(autouse=True)
    def setup(self, admin_user, db):
        self.admin = admin_user
        self.factory = RequestFactory()
        
        # Create some advisors
        self.advisor1 = User.objects.create_user(
            email='advisor1@test.com',
            username='advisor1',
            password='testpass123',
            role='advisor',
            is_active=True
        )
        self.advisor2 = User.objects.create_user(
            email='advisor2@test.com',
            username='advisor2',
            password='testpass123',
            role='advisor',
            is_active=False
        )
    
    def test_advisor_list_returns_advisors(self):
        """Test advisor_list returns correct context"""
        from eduAPI.views.advisor_management import advisor_list
        
        request = self.factory.get('/advisors/')
        request.user = self.admin
        add_middleware_to_request(request)
        
        response = advisor_list(request)
        assert response.status_code == 200


@pytest.mark.django_db
class TestCreateAdvisorView:
    """Tests for create_advisor view function"""
    
    @pytest.fixture(autouse=True)
    def setup(self, admin_user, db):
        self.admin = admin_user
        self.factory = RequestFactory()
    
    def test_create_advisor_get(self):
        """Test create advisor GET request"""
        from eduAPI.views.advisor_management import create_advisor
        
        request = self.factory.get('/advisors/create/')
        request.user = self.admin
        add_middleware_to_request(request)
        
        response = create_advisor(request)
        assert response.status_code == 200
    
    def test_create_advisor_post_success(self):
        """Test successful advisor creation"""
        from eduAPI.views.advisor_management import create_advisor
        
        request = self.factory.post('/advisors/create/', {
            'email': 'newadvisor@test.com',
            'first_name': 'New',
            'last_name': 'Advisor',
            'password': 'securepass123'
        })
        request.user = self.admin
        add_middleware_to_request(request)
        
        response = create_advisor(request)
        assert response.status_code == 302  # Redirect on success
        assert User.objects.filter(email='newadvisor@test.com').exists()
    
    def test_create_advisor_duplicate_email(self):
        """Test error when creating advisor with existing email"""
        from eduAPI.views.advisor_management import create_advisor
        
        # Create existing user
        User.objects.create_user(
            email='existing@test.com',
            username='existing',
            password='testpass123'
        )
        
        request = self.factory.post('/advisors/create/', {
            'email': 'existing@test.com',
            'first_name': 'Test',
            'last_name': 'User',
            'password': 'testpass123'
        })
        request.user = self.admin
        add_middleware_to_request(request)
        
        response = create_advisor(request)
        assert response.status_code == 302  # Redirect with error message


@pytest.mark.django_db
class TestDeleteAdvisorView:
    """Tests for delete_advisor view function"""
    
    @pytest.fixture(autouse=True)
    def setup(self, admin_user, db):
        self.admin = admin_user
        self.factory = RequestFactory()
        
        self.advisor = User.objects.create_user(
            email='todelete@test.com',
            username='todelete',
            password='testpass123',
            role='advisor'
        )
    
    def test_delete_advisor_get(self):
        """Test delete confirmation page"""
        from eduAPI.views.advisor_management import delete_advisor
        
        request = self.factory.get(f'/advisors/delete/{self.advisor.id}/')
        request.user = self.admin
        add_middleware_to_request(request)
        
        response = delete_advisor(request, self.advisor.id)
        assert response.status_code == 200
    
    def test_delete_advisor_post_success(self):
        """Test successful advisor deletion"""
        from eduAPI.views.advisor_management import delete_advisor
        
        advisor_id = self.advisor.id
        request = self.factory.post(f'/advisors/delete/{advisor_id}/')
        request.user = self.admin
        add_middleware_to_request(request)
        
        response = delete_advisor(request, advisor_id)
        assert response.status_code == 302  # Redirect on success
        assert not User.objects.filter(id=advisor_id).exists()


@pytest.mark.django_db
class TestResetPasswordView:
    """Tests for reset_password view function"""
    
    @pytest.fixture(autouse=True)
    def setup(self, admin_user, db):
        self.admin = admin_user
        self.factory = RequestFactory()
        
        self.advisor = User.objects.create_user(
            email='resetpass@test.com',
            username='resetpass',
            password='oldpassword123',
            role='advisor'
        )
    
    def test_reset_password_get(self):
        """Test reset password form display"""
        from eduAPI.views.advisor_management import reset_password
        
        request = self.factory.get(f'/advisors/reset-password/{self.advisor.id}/')
        request.user = self.admin
        add_middleware_to_request(request)
        
        response = reset_password(request, self.advisor.id)
        assert response.status_code == 200
    
    def test_reset_password_success(self):
        """Test successful password reset"""
        from eduAPI.views.advisor_management import reset_password
        
        request = self.factory.post(f'/advisors/reset-password/{self.advisor.id}/', {
            'new_password': 'newpassword123',
            'confirm_password': 'newpassword123'
        })
        request.user = self.admin
        add_middleware_to_request(request)
        
        response = reset_password(request, self.advisor.id)
        assert response.status_code == 302  # Redirect on success
        
        self.advisor.refresh_from_db()
        assert self.advisor.check_password('newpassword123')
    
    def test_reset_password_empty(self):
        """Test error when password is empty"""
        from eduAPI.views.advisor_management import reset_password
        
        request = self.factory.post(f'/advisors/reset-password/{self.advisor.id}/', {
            'new_password': '',
            'confirm_password': ''
        })
        request.user = self.admin
        add_middleware_to_request(request)
        
        response = reset_password(request, self.advisor.id)
        assert response.status_code == 200  # Stay on page with error
    
    def test_reset_password_too_short(self):
        """Test error when password is too short"""
        from eduAPI.views.advisor_management import reset_password
        
        request = self.factory.post(f'/advisors/reset-password/{self.advisor.id}/', {
            'new_password': 'short',
            'confirm_password': 'short'
        })
        request.user = self.admin
        add_middleware_to_request(request)
        
        response = reset_password(request, self.advisor.id)
        assert response.status_code == 200  # Stay on page with error
    
    def test_reset_password_mismatch(self):
        """Test error when passwords don't match"""
        from eduAPI.views.advisor_management import reset_password
        
        request = self.factory.post(f'/advisors/reset-password/{self.advisor.id}/', {
            'new_password': 'newpassword123',
            'confirm_password': 'differentpassword'
        })
        request.user = self.admin
        add_middleware_to_request(request)
        
        response = reset_password(request, self.advisor.id)
        assert response.status_code == 200  # Stay on page with error


@pytest.mark.django_db
class TestToggleAdvisorStatusView:
    """Tests for toggle_advisor_status view function"""
    
    @pytest.fixture(autouse=True)
    def setup(self, admin_user, db):
        self.admin = admin_user
        self.factory = RequestFactory()
        
        self.advisor = User.objects.create_user(
            email='toggle@test.com',
            username='toggle',
            password='testpass123',
            role='advisor',
            is_active=True
        )
    
    def test_toggle_status_deactivate(self):
        """Test deactivating an active advisor"""
        from eduAPI.views.advisor_management import toggle_advisor_status
        
        request = self.factory.get(f'/advisors/toggle-status/{self.advisor.id}/')
        request.user = self.admin
        add_middleware_to_request(request)
        
        response = toggle_advisor_status(request, self.advisor.id)
        assert response.status_code == 302  # Redirect
        
        self.advisor.refresh_from_db()
        assert self.advisor.is_active is False
    
    def test_toggle_status_activate(self):
        """Test activating an inactive advisor"""
        from eduAPI.views.advisor_management import toggle_advisor_status
        
        self.advisor.is_active = False
        self.advisor.save()
        
        request = self.factory.get(f'/advisors/toggle-status/{self.advisor.id}/')
        request.user = self.admin
        add_middleware_to_request(request)
        
        response = toggle_advisor_status(request, self.advisor.id)
        assert response.status_code == 302  # Redirect
        
        self.advisor.refresh_from_db()
        assert self.advisor.is_active is True


@pytest.mark.django_db
class TestAdvisorStatsView:
    """Tests for advisor_stats view function"""
    
    @pytest.fixture(autouse=True)
    def setup(self, admin_user, db):
        self.admin = admin_user
        self.factory = RequestFactory()
        
        # Create advisors
        User.objects.create_user(
            email='active1@test.com',
            username='active1',
            password='testpass123',
            role='advisor',
            is_active=True
        )
        User.objects.create_user(
            email='active2@test.com',
            username='active2',
            password='testpass123',
            role='advisor',
            is_active=True
        )
        User.objects.create_user(
            email='inactive@test.com',
            username='inactive',
            password='testpass123',
            role='advisor',
            is_active=False
        )
    
    def test_advisor_stats_success(self):
        """Test advisor stats returns correct JSON"""
        from eduAPI.views.advisor_management import advisor_stats
        
        request = self.factory.get('/advisors/stats/')
        request.user = self.admin
        add_middleware_to_request(request)
        
        response = advisor_stats(request)
        assert response.status_code == 200
        
        import json
        data = json.loads(response.content)
        assert 'total_advisors' in data
        assert 'active_advisors' in data
        assert 'inactive_advisors' in data
    
    def test_advisor_stats_counts(self):
        """Test advisor stats returns correct counts"""
        from eduAPI.views.advisor_management import advisor_stats
        
        request = self.factory.get('/advisors/stats/')
        request.user = self.admin
        add_middleware_to_request(request)
        
        response = advisor_stats(request)
        
        import json
        data = json.loads(response.content)
        
        assert data['total_advisors'] == 3
        assert data['active_advisors'] == 2
        assert data['inactive_advisors'] == 1
