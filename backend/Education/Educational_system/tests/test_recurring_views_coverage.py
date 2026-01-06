# Tests for recurring_sessions_views.py to increase coverage
import pytest
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta

User = get_user_model()


class TestSessionTemplateViewSetExtended(TestCase):
    """Extended tests for SessionTemplateViewSet"""
    
    def setUp(self):
        self.client = APIClient()
        self.teacher = User.objects.create_user(
            username='teacher_rv1',
            email='teacher@test.com',
            password='testpass123',
            first_name='Test',
            last_name='Teacher',
            role='teacher',
            is_email_verified=True
        )
        self.teacher2 = User.objects.create_user(
            username='teacher_rv2',
            email='teacher2@test.com',
            password='testpass123',
            first_name='Test2',
            last_name='Teacher2',
            role='teacher',
            is_email_verified=True
        )
        self.advisor = User.objects.create_user(
            username='advisor_rv1',
            email='advisor@test.com',
            password='testpass123',
            first_name='Test',
            last_name='Advisor',
            role='advisor',
            is_email_verified=True
        )
        self.student = User.objects.create_user(
            username='student_rv1',
            email='student@test.com',
            password='testpass123',
            first_name='Test',
            last_name='Student',
            role='student',
            is_email_verified=True
        )
    
    def test_get_queryset_as_student(self):
        """Test that students get empty queryset"""
        from eduAPI.models.recurring_sessions_models import SessionTemplate
        
        SessionTemplate.objects.create(
            title='Test Template',
            teacher=self.teacher,
            subject='Math',
            level='10',
            day_of_week=1,
            start_time='10:00:00',
            recurrence_type='WEEKLY',
            status='ACTIVE',
            start_date=timezone.now().date()
        )
        
        self.client.force_authenticate(user=self.student)
        response = self.client.get('/api/recurring-sessions/templates/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)
    
    def test_pause_template_not_owner(self):
        """Test pausing template by non-owner returns 404 (not in their queryset)"""
        from eduAPI.models.recurring_sessions_models import SessionTemplate
        
        template = SessionTemplate.objects.create(
            title='Test Template',
            teacher=self.teacher,
            subject='Math',
            level='10',
            day_of_week=1,
            start_time='10:00:00',
            recurrence_type='WEEKLY',
            status='ACTIVE',
            start_date=timezone.now().date()
        )
        
        # Teacher2 can't see teacher1's templates, so gets 404
        self.client.force_authenticate(user=self.teacher2)
        response = self.client.post(f'/api/recurring-sessions/templates/{template.id}/pause/')
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_resume_template_not_owner(self):
        """Test resuming template by non-owner returns 404"""
        from eduAPI.models.recurring_sessions_models import SessionTemplate
        
        template = SessionTemplate.objects.create(
            title='Test Template',
            teacher=self.teacher,
            subject='Math',
            level='10',
            day_of_week=1,
            start_time='10:00:00',
            recurrence_type='WEEKLY',
            status='PAUSED',
            start_date=timezone.now().date()
        )
        
        self.client.force_authenticate(user=self.teacher2)
        response = self.client.post(f'/api/recurring-sessions/templates/{template.id}/resume/')
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_end_template_not_owner(self):
        """Test ending template by non-owner returns 404"""
        from eduAPI.models.recurring_sessions_models import SessionTemplate
        
        template = SessionTemplate.objects.create(
            title='Test Template',
            teacher=self.teacher,
            subject='Math',
            level='10',
            day_of_week=1,
            start_time='10:00:00',
            recurrence_type='WEEKLY',
            status='ACTIVE',
            start_date=timezone.now().date()
        )
        
        self.client.force_authenticate(user=self.teacher2)
        response = self.client.post(f'/api/recurring-sessions/templates/{template.id}/end/')
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_pause_template_success(self):
        """Test pausing own template successfully"""
        from eduAPI.models.recurring_sessions_models import SessionTemplate
        
        template = SessionTemplate.objects.create(
            title='Test Template',
            teacher=self.teacher,
            subject='Math',
            level='10',
            day_of_week=1,
            start_time='10:00:00',
            recurrence_type='WEEKLY',
            status='ACTIVE',
            start_date=timezone.now().date()
        )
        
        self.client.force_authenticate(user=self.teacher)
        response = self.client.post(f'/api/recurring-sessions/templates/{template.id}/pause/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        template.refresh_from_db()
        self.assertEqual(template.status, 'PAUSED')
    
    def test_resume_template_success(self):
        """Test resuming own template successfully"""
        from eduAPI.models.recurring_sessions_models import SessionTemplate
        
        template = SessionTemplate.objects.create(
            title='Test Template',
            teacher=self.teacher,
            subject='Math',
            level='10',
            day_of_week=1,
            start_time='10:00:00',
            recurrence_type='WEEKLY',
            status='PAUSED',
            start_date=timezone.now().date()
        )
        
        self.client.force_authenticate(user=self.teacher)
        response = self.client.post(f'/api/recurring-sessions/templates/{template.id}/resume/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        template.refresh_from_db()
        self.assertEqual(template.status, 'ACTIVE')
    
    def test_end_template_success(self):
        """Test ending own template successfully"""
        from eduAPI.models.recurring_sessions_models import SessionTemplate
        
        template = SessionTemplate.objects.create(
            title='Test Template',
            teacher=self.teacher,
            subject='Math',
            level='10',
            day_of_week=1,
            start_time='10:00:00',
            recurrence_type='WEEKLY',
            status='ACTIVE',
            start_date=timezone.now().date()
        )
        
        self.client.force_authenticate(user=self.teacher)
        response = self.client.post(f'/api/recurring-sessions/templates/{template.id}/end/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        template.refresh_from_db()
        self.assertEqual(template.status, 'ENDED')
    
    def test_assignments_get(self):
        """Test getting assignments for a template"""
        from eduAPI.models.recurring_sessions_models import SessionTemplate
        
        template = SessionTemplate.objects.create(
            title='Test Template',
            teacher=self.teacher,
            subject='Math',
            level='10',
            day_of_week=1,
            start_time='10:00:00',
            recurrence_type='WEEKLY',
            status='ACTIVE',
            start_date=timezone.now().date()
        )
        
        self.client.force_authenticate(user=self.teacher)
        response = self.client.get(f'/api/recurring-sessions/templates/{template.id}/assignments/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_assignments_post_not_advisor(self):
        """Test creating assignments by non-advisor"""
        from eduAPI.models.recurring_sessions_models import SessionTemplate
        
        template = SessionTemplate.objects.create(
            title='Test Template',
            teacher=self.teacher,
            subject='Math',
            level='10',
            day_of_week=1,
            start_time='10:00:00',
            recurrence_type='WEEKLY',
            status='ACTIVE',
            start_date=timezone.now().date()
        )
        
        self.client.force_authenticate(user=self.teacher)
        response = self.client.post(
            f'/api/recurring-sessions/templates/{template.id}/assignments/',
            {'student_ids': [self.student.id]}
        )
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_assignments_post_no_students(self):
        """Test creating assignments with no students"""
        from eduAPI.models.recurring_sessions_models import SessionTemplate
        
        template = SessionTemplate.objects.create(
            title='Test Template',
            teacher=self.teacher,
            subject='Math',
            level='10',
            day_of_week=1,
            start_time='10:00:00',
            recurrence_type='WEEKLY',
            status='ACTIVE',
            start_date=timezone.now().date()
        )
        
        self.client.force_authenticate(user=self.advisor)
        response = self.client.post(
            f'/api/recurring-sessions/templates/{template.id}/assignments/',
            {'student_ids': []}
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_assignments_post_success(self):
        """Test creating assignments successfully"""
        from eduAPI.models.recurring_sessions_models import SessionTemplate
        
        template = SessionTemplate.objects.create(
            title='Test Template',
            teacher=self.teacher,
            subject='Math',
            level='10',
            day_of_week=1,
            start_time='10:00:00',
            recurrence_type='WEEKLY',
            status='ACTIVE',
            start_date=timezone.now().date()
        )
        
        self.client.force_authenticate(user=self.advisor)
        response = self.client.post(
            f'/api/recurring-sessions/templates/{template.id}/assignments/',
            {'student_ids': [self.student.id]},
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('assigned_count', response.data)
    
    def test_assigned_students(self):
        """Test getting assigned students"""
        from eduAPI.models.recurring_sessions_models import SessionTemplate, StudentGroup, TemplateGroupAssignment
        
        template = SessionTemplate.objects.create(
            title='Test Template',
            teacher=self.teacher,
            subject='Math',
            level='10',
            day_of_week=1,
            start_time='10:00:00',
            recurrence_type='WEEKLY',
            status='ACTIVE',
            start_date=timezone.now().date()
        )
        
        group = StudentGroup.objects.create(
            name='Test Group',
            advisor=self.advisor,
            is_active=True
        )
        group.students.add(self.student)
        
        TemplateGroupAssignment.objects.create(
            template=template,
            group=group,
            advisor=self.advisor,
            is_active=True
        )
        
        self.client.force_authenticate(user=self.teacher)
        response = self.client.get(f'/api/recurring-sessions/templates/{template.id}/assigned_students/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
    
    def test_unassign_not_advisor(self):
        """Test unassigning by non-advisor"""
        from eduAPI.models.recurring_sessions_models import SessionTemplate
        
        template = SessionTemplate.objects.create(
            title='Test Template',
            teacher=self.teacher,
            subject='Math',
            level='10',
            day_of_week=1,
            start_time='10:00:00',
            recurrence_type='WEEKLY',
            status='ACTIVE',
            start_date=timezone.now().date()
        )
        
        self.client.force_authenticate(user=self.teacher)
        response = self.client.post(
            f'/api/recurring-sessions/templates/{template.id}/unassign/',
            {'student_ids': [self.student.id]}
        )
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_unassign_no_students(self):
        """Test unassigning with no students"""
        from eduAPI.models.recurring_sessions_models import SessionTemplate
        
        template = SessionTemplate.objects.create(
            title='Test Template',
            teacher=self.teacher,
            subject='Math',
            level='10',
            day_of_week=1,
            start_time='10:00:00',
            recurrence_type='WEEKLY',
            status='ACTIVE',
            start_date=timezone.now().date()
        )
        
        self.client.force_authenticate(user=self.advisor)
        response = self.client.post(
            f'/api/recurring-sessions/templates/{template.id}/unassign/',
            {'student_ids': []}
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_simple_templates(self):
        """Test getting simple template list"""
        from eduAPI.models.recurring_sessions_models import SessionTemplate
        
        SessionTemplate.objects.create(
            title='Test Template',
            teacher=self.teacher,
            subject='Math',
            level='10',
            day_of_week=1,
            start_time='10:00:00',
            recurrence_type='WEEKLY',
            status='ACTIVE',
            start_date=timezone.now().date()
        )
        
        self.client.force_authenticate(user=self.teacher)
        response = self.client.get('/api/recurring-sessions/templates/simple/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class TestStudentGroupViewSetExtended(TestCase):
    """Extended tests for StudentGroupViewSet"""
    
    def setUp(self):
        self.client = APIClient()
        self.advisor = User.objects.create_user(
            username='advisor_sg1',
            email='advisor@test.com',
            password='testpass123',
            first_name='Test',
            last_name='Advisor',
            role='advisor',
            is_email_verified=True
        )
        self.student = User.objects.create_user(
            username='student_sg1',
            email='student@test.com',
            password='testpass123',
            first_name='Test',
            last_name='Student',
            role='student',
            is_email_verified=True
        )
        self.teacher = User.objects.create_user(
            username='teacher_sg1',
            email='teacher@test.com',
            password='testpass123',
            first_name='Test',
            last_name='Teacher',
            role='teacher',
            is_email_verified=True
        )
    
    def test_get_queryset_as_non_advisor(self):
        """Test that non-advisors get empty queryset"""
        from eduAPI.models.recurring_sessions_models import StudentGroup
        
        StudentGroup.objects.create(
            name='Test Group',
            advisor=self.advisor,
            is_active=True
        )
        
        self.client.force_authenticate(user=self.teacher)
        response = self.client.get('/api/recurring-sessions/groups/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)
    
    def test_add_students(self):
        """Test adding students to a group"""
        from eduAPI.models.recurring_sessions_models import StudentGroup
        
        group = StudentGroup.objects.create(
            name='Test Group',
            advisor=self.advisor,
            is_active=True
        )
        
        self.client.force_authenticate(user=self.advisor)
        response = self.client.post(
            f'/api/recurring-sessions/groups/{group.id}/add_students/',
            {'student_ids': [self.student.id]},
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total_students'], 1)
    
    def test_remove_students(self):
        """Test removing students from a group"""
        from eduAPI.models.recurring_sessions_models import StudentGroup
        
        group = StudentGroup.objects.create(
            name='Test Group',
            advisor=self.advisor,
            is_active=True
        )
        group.students.add(self.student)
        
        self.client.force_authenticate(user=self.advisor)
        response = self.client.post(
            f'/api/recurring-sessions/groups/{group.id}/remove_students/',
            {'student_ids': [self.student.id]},
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total_students'], 0)
    
    def test_template_assignments(self):
        """Test getting template assignments for a group"""
        from eduAPI.models.recurring_sessions_models import StudentGroup
        
        group = StudentGroup.objects.create(
            name='Test Group',
            advisor=self.advisor,
            is_active=True
        )
        
        self.client.force_authenticate(user=self.advisor)
        response = self.client.get(f'/api/recurring-sessions/groups/{group.id}/template_assignments/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_simple_groups(self):
        """Test getting simple group list"""
        from eduAPI.models.recurring_sessions_models import StudentGroup
        
        StudentGroup.objects.create(
            name='Test Group',
            advisor=self.advisor,
            is_active=True
        )
        
        self.client.force_authenticate(user=self.advisor)
        response = self.client.get('/api/recurring-sessions/groups/simple/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class TestTemplateGroupAssignmentViewSetExtended(TestCase):
    """Extended tests for TemplateGroupAssignmentViewSet"""
    
    def setUp(self):
        self.client = APIClient()
        self.teacher = User.objects.create_user(
            username='teacher_tga1',
            email='teacher@test.com',
            password='testpass123',
            first_name='Test',
            last_name='Teacher',
            role='teacher',
            is_email_verified=True
        )
        self.advisor = User.objects.create_user(
            username='advisor_tga1',
            email='advisor@test.com',
            password='testpass123',
            first_name='Test',
            last_name='Advisor',
            role='advisor',
            is_email_verified=True
        )
        self.advisor2 = User.objects.create_user(
            username='advisor_tga2',
            email='advisor2@test.com',
            password='testpass123',
            first_name='Test2',
            last_name='Advisor2',
            role='advisor',
            is_email_verified=True
        )
        self.student = User.objects.create_user(
            username='student_tga1',
            email='student@test.com',
            password='testpass123',
            first_name='Test',
            last_name='Student',
            role='student',
            is_email_verified=True
        )
    
    def test_get_queryset_as_teacher(self):
        """Test teacher sees assignments to their templates"""
        from eduAPI.models.recurring_sessions_models import SessionTemplate, StudentGroup, TemplateGroupAssignment
        
        template = SessionTemplate.objects.create(
            title='Test Template',
            teacher=self.teacher,
            subject='Math',
            level='10',
            day_of_week=1,
            start_time='10:00:00',
            recurrence_type='WEEKLY',
            status='ACTIVE',
            start_date=timezone.now().date()
        )
        
        group = StudentGroup.objects.create(
            name='Test Group',
            advisor=self.advisor,
            is_active=True
        )
        
        TemplateGroupAssignment.objects.create(
            template=template,
            group=group,
            advisor=self.advisor,
            is_active=True
        )
        
        self.client.force_authenticate(user=self.teacher)
        response = self.client.get('/api/recurring-sessions/assignments/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
    
    def test_deactivate_assignment_not_owner(self):
        """Test deactivating assignment by non-owner returns 404"""
        from eduAPI.models.recurring_sessions_models import SessionTemplate, StudentGroup, TemplateGroupAssignment
        
        template = SessionTemplate.objects.create(
            title='Test Template',
            teacher=self.teacher,
            subject='Math',
            level='10',
            day_of_week=1,
            start_time='10:00:00',
            recurrence_type='WEEKLY',
            status='ACTIVE',
            start_date=timezone.now().date()
        )
        
        group = StudentGroup.objects.create(
            name='Test Group',
            advisor=self.advisor,
            is_active=True
        )
        
        assignment = TemplateGroupAssignment.objects.create(
            template=template,
            group=group,
            advisor=self.advisor,
            is_active=True
        )
        
        # advisor2 can't see advisor1's assignments
        self.client.force_authenticate(user=self.advisor2)
        response = self.client.post(f'/api/recurring-sessions/assignments/{assignment.id}/deactivate/')
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_reactivate_assignment_not_owner(self):
        """Test reactivating assignment by non-owner returns 404"""
        from eduAPI.models.recurring_sessions_models import SessionTemplate, StudentGroup, TemplateGroupAssignment
        
        template = SessionTemplate.objects.create(
            title='Test Template',
            teacher=self.teacher,
            subject='Math',
            level='10',
            day_of_week=1,
            start_time='10:00:00',
            recurrence_type='WEEKLY',
            status='ACTIVE',
            start_date=timezone.now().date()
        )
        
        group = StudentGroup.objects.create(
            name='Test Group',
            advisor=self.advisor,
            is_active=True
        )
        
        assignment = TemplateGroupAssignment.objects.create(
            template=template,
            group=group,
            advisor=self.advisor,
            is_active=False
        )
        
        self.client.force_authenticate(user=self.advisor2)
        response = self.client.post(f'/api/recurring-sessions/assignments/{assignment.id}/reactivate/')
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_deactivate_assignment_success(self):
        """Test deactivating own assignment successfully"""
        from eduAPI.models.recurring_sessions_models import SessionTemplate, StudentGroup, TemplateGroupAssignment
        
        template = SessionTemplate.objects.create(
            title='Test Template',
            teacher=self.teacher,
            subject='Math',
            level='10',
            day_of_week=1,
            start_time='10:00:00',
            recurrence_type='WEEKLY',
            status='ACTIVE',
            start_date=timezone.now().date()
        )
        
        group = StudentGroup.objects.create(
            name='Test Group',
            advisor=self.advisor,
            is_active=True
        )
        
        assignment = TemplateGroupAssignment.objects.create(
            template=template,
            group=group,
            advisor=self.advisor,
            is_active=True
        )
        
        self.client.force_authenticate(user=self.advisor)
        response = self.client.post(f'/api/recurring-sessions/assignments/{assignment.id}/deactivate/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_reactivate_assignment_success(self):
        """Test reactivating own assignment successfully"""
        from eduAPI.models.recurring_sessions_models import SessionTemplate, StudentGroup, TemplateGroupAssignment
        
        template = SessionTemplate.objects.create(
            title='Test Template',
            teacher=self.teacher,
            subject='Math',
            level='10',
            day_of_week=1,
            start_time='10:00:00',
            recurrence_type='WEEKLY',
            status='ACTIVE',
            start_date=timezone.now().date()
        )
        
        group = StudentGroup.objects.create(
            name='Test Group',
            advisor=self.advisor,
            is_active=True
        )
        
        assignment = TemplateGroupAssignment.objects.create(
            template=template,
            group=group,
            advisor=self.advisor,
            is_active=False
        )
        
        self.client.force_authenticate(user=self.advisor)
        response = self.client.post(f'/api/recurring-sessions/assignments/{assignment.id}/reactivate/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class TestGeneratedSessionViewSet(TestCase):
    """Tests for GeneratedSessionViewSet"""
    
    def setUp(self):
        self.client = APIClient()
        self.teacher = User.objects.create_user(
            username='teacher_gs1',
            email='teacher@test.com',
            password='testpass123',
            first_name='Test',
            last_name='Teacher',
            role='teacher',
            is_email_verified=True
        )
        self.student = User.objects.create_user(
            username='student_gs1',
            email='student@test.com',
            password='testpass123',
            first_name='Test',
            last_name='Student',
            role='student',
            is_email_verified=True
        )
    
    def test_get_queryset_as_student(self):
        """Test student sees their assigned sessions"""
        self.client.force_authenticate(user=self.student)
        response = self.client.get('/api/recurring-sessions/generated-sessions/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class TestTemplateGenerationLogViewSet(TestCase):
    """Tests for TemplateGenerationLogViewSet"""
    
    def setUp(self):
        self.client = APIClient()
        self.teacher = User.objects.create_user(
            username='teacher_tgl1',
            email='teacher@test.com',
            password='testpass123',
            first_name='Test',
            last_name='Teacher',
            role='teacher',
            is_email_verified=True
        )
        self.student = User.objects.create_user(
            username='student_tgl1',
            email='student@test.com',
            password='testpass123',
            first_name='Test',
            last_name='Student',
            role='student',
            is_email_verified=True
        )
    
    def test_get_queryset_as_non_teacher(self):
        """Test non-teacher gets empty queryset"""
        self.client.force_authenticate(user=self.student)
        response = self.client.get('/api/recurring-sessions/generation-logs/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)


class TestUtilityViews(TestCase):
    """Tests for utility views"""
    
    def setUp(self):
        self.client = APIClient()
        self.advisor = User.objects.create_user(
            username='advisor_uv1',
            email='advisor@test.com',
            password='testpass123',
            first_name='Test',
            last_name='Advisor',
            role='advisor',
            is_email_verified=True
        )
        self.teacher = User.objects.create_user(
            username='teacher_uv1',
            email='teacher@test.com',
            password='testpass123',
            first_name='Test',
            last_name='Teacher',
            role='teacher',
            is_email_verified=True
        )
        self.student = User.objects.create_user(
            username='student_uv1',
            email='student@test.com',
            password='testpass123',
            first_name='Test',
            last_name='Student',
            role='student',
            is_email_verified=True
        )
    
    def test_get_available_students_not_advisor(self):
        """Test get_available_students by non-advisor"""
        self.client.force_authenticate(user=self.teacher)
        response = self.client.get('/api/recurring-sessions/students/available/')
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_get_available_students_with_search(self):
        """Test get_available_students with search"""
        self.client.force_authenticate(user=self.advisor)
        response = self.client.get('/api/recurring-sessions/students/available/?search=Test')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_get_my_recurring_sessions_not_student(self):
        """Test get_my_recurring_sessions by non-student"""
        self.client.force_authenticate(user=self.teacher)
        response = self.client.get('/api/recurring-sessions/my-sessions/')
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_get_my_recurring_sessions_as_student(self):
        """Test get_my_recurring_sessions as student"""
        self.client.force_authenticate(user=self.student)
        response = self.client.get('/api/recurring-sessions/my-sessions/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_get_template_statistics_as_teacher(self):
        """Test get_template_statistics as teacher"""
        self.client.force_authenticate(user=self.teacher)
        response = self.client.get('/api/recurring-sessions/statistics/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_templates', response.data)
    
    def test_get_template_statistics_as_advisor(self):
        """Test get_template_statistics as advisor"""
        self.client.force_authenticate(user=self.advisor)
        response = self.client.get('/api/recurring-sessions/statistics/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_get_template_statistics_as_student(self):
        """Test get_template_statistics as student (forbidden)"""
        self.client.force_authenticate(user=self.student)
        response = self.client.get('/api/recurring-sessions/statistics/')
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
